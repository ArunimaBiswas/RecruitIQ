from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from models import db, Job, Candidate, Application, Interview
from agents.jd_summarizer import JDSummarizer
from agents.resume_parser import ResumeParserAgent
from agents.matcher import Matcher
from agents.scheduler import Scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recruitment.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize agents
jd_summarizer = JDSummarizer()
resume_parser = ResumeParserAgent()

# Get the absolute path to the model directory
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(os.path.dirname(current_dir), 'distilbert_resume_matcher')
logger.info(f"Loading model from: {model_path}")

matcher = Matcher(model_path)
scheduler = Scheduler()

@app.route("/api/jobs", methods=["POST"])
def create_job():
    """Create a new job posting"""
    try:
        data = request.json
        if not data or "title" not in data or "description" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Generate JD summary
        summary = jd_summarizer.summarize(data["description"])
        
        # Create job record
        job = Job(
            title=data["title"],
            description=data["description"],
            summary=summary
        )
        db.session.add(job)
        db.session.commit()

        return jsonify({
            "job_id": job.job_id,
            "message": "Job created successfully"
        }), 201

    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/apply", methods=["POST"])
def apply_to_job():
    """Process a job application"""
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        resume_file = request.files["resume"]
        if resume_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Save resume
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(resume_path)

        # Parse resume
        parsed_data = resume_parser.parse(resume_path)

        # Create candidate record
        candidate = Candidate(
            name=request.form["name"],
            email=request.form["email"],
            resume_path=resume_path,
            parsed_data=parsed_data
        )
        db.session.add(candidate)
        db.session.commit()

        # Get job details
        job = Job.query.get(request.form["job_id"])
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Compute match score
        match_score = matcher.compute_match(job.summary, parsed_data)

        # Create application record
        application = Application(
            job_id=job.job_id,
            candidate_id=candidate.candidate_id,
            match_score=match_score
        )
        db.session.add(application)
        db.session.commit()

        return jsonify({
            "application_id": application.application_id,
            "match_score": match_score,
            "message": "Application submitted successfully"
        }), 201

    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/jobs/<int:job_id>/candidates", methods=["GET"])
def get_candidates(job_id):
    """Get all candidates for a job"""
    try:
        applications = Application.query.filter_by(job_id=job_id).all()
        candidates = []
        
        for app in applications:
            candidate = app.candidate
            match_details = matcher.get_match_details(
                app.job.summary,
                candidate.parsed_data
            )
            
            candidates.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "email": candidate.email,
                "match_score": app.match_score,
                "status": app.status,
                "match_details": match_details
            })
        
        return jsonify(candidates)

    except Exception as e:
        logger.error(f"Error fetching candidates: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/schedule", methods=["POST"])
def schedule_interview():
    """Schedule an interview"""
    try:
        data = request.json
        application_id = data.get("application_id")
        
        if not application_id:
            return jsonify({"error": "Missing application_id"}), 400

        # Get application details
        application = Application.query.get(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404

        # Schedule interview
        result = scheduler.schedule(
            application_id,
            application.candidate.email,
            application.job.title
        )

        if result["status"] == "scheduled":
            # Create interview record
            interview = Interview(
                application_id=application_id,
                interview_time=datetime.fromisoformat(result["interview_time"]),
                status="scheduled"
            )
            db.session.add(interview)
            
            # Update application status
            application.status = "interview_scheduled"
            db.session.commit()

            return jsonify({
                "interview_id": interview.interview_id,
                "interview_time": result["interview_time"],
                "message": "Interview scheduled successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to schedule interview"}), 500

    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000) 