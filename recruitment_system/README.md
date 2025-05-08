# AI-Powered Recruitment System

An intelligent recruitment system that uses AI to match resumes with job descriptions and automate the hiring process.

## Features

- **JD Summarization**: Automatically extracts key requirements from job descriptions
- **Resume Parsing**: Intelligently parses PDF resumes and extracts relevant information
- **AI Matching**: Uses DistilBERT to compute match scores between resumes and jobs
- **Interview Scheduling**: Automated interview scheduling with email notifications
- **User-Friendly Interface**: Streamlit-based dashboard for easy interaction

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Streamlit
- **AI/ML**: PyTorch, Transformers (DistilBERT)
- **NLP**: NLTK
- **PDF Processing**: pdfplumber
- **Database**: SQLite

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

4. Initialize the database:
```bash
python app.py
```

## Running the Application

1. Start the Flask backend:
```bash
python app.py
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```

3. Access the application:
- Backend API: http://localhost:5000
- Frontend: http://localhost:8501

## Usage

1. **Create a Job**:
   - Enter job title and description
   - System automatically extracts key requirements

2. **Apply for Jobs**:
   - Upload resume (PDF)
   - System parses resume and computes match score

3. **View Candidates**:
   - See all applicants for a job
   - View detailed match analysis
   - Compare skills and qualifications

4. **Schedule Interviews**:
   - Select candidates for interviews
   - System automatically sends email invitations

## Model Integration

The system uses a pre-trained DistilBERT model for resume-JD matching. The model has been trained on a dataset of labeled resume-JD pairs and achieves 85% accuracy.

To use your own trained model:
1. Place your model in the `models` directory
2. Update the model path in `app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 