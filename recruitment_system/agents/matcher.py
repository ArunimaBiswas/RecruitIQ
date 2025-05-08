import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, AutoModelForSequenceClassification
import json
import logging
import os

class Matcher:
    def __init__(self, model_path=None):
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize tokenizer
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        
        # Load model
        try:
            if model_path and os.path.exists(model_path):
                self.logger.info(f"Loading model from: {model_path}")
                # Use AutoModelForSequenceClassification to handle different model formats
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_path,
                    local_files_only=True,
                    trust_remote_code=True
                )
            else:
                self.logger.warning(f"Model path not found: {model_path}. Using default model.")
                self.model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')
            
            self.model.to(self.device)
            self.model.eval()
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            self.logger.info("Using default model as fallback")
            self.model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')
            self.model.to(self.device)
            self.model.eval()

    def prepare_input(self, jd_summary, parsed_resume):
        """Prepare input for the model"""
        try:
            # Parse JSON strings if needed
            if isinstance(jd_summary, str):
                jd_summary = json.loads(jd_summary)
            if isinstance(parsed_resume, str):
                parsed_resume = json.loads(parsed_resume)

            # Combine JD and resume text
            jd_text = jd_summary.get('processed_text', '')
            resume_text = parsed_resume.get('processed_text', '')
            
            # Format input as in training
            input_text = f"[CLS] {jd_text} [SEP] {resume_text} [SEP]"
            
            # Tokenize
            inputs = self.tokenizer(
                input_text,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding='max_length'
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            return inputs
            
        except Exception as e:
            self.logger.error(f"Error preparing input: {str(e)}")
            return None

    def compute_match(self, jd_summary, parsed_resume):
        """Compute match score between JD and resume"""
        try:
            inputs = self.prepare_input(jd_summary, parsed_resume)
            if inputs is None:
                return 0.0

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Get the probabilities using softmax
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
                # Get the probability of the positive class (index 1)
                match_score = probabilities[0][1].item()
                
            return match_score
            
        except Exception as e:
            self.logger.error(f"Error computing match score: {str(e)}")
            return 0.0

    def get_match_details(self, jd_summary, parsed_resume):
        """Get detailed matching information"""
        try:
            # Parse JSON strings if needed
            if isinstance(jd_summary, str):
                jd_summary = json.loads(jd_summary)
            if isinstance(parsed_resume, str):
                parsed_resume = json.loads(parsed_resume)

            # Get match score
            match_score = self.compute_match(jd_summary, parsed_resume)

            # Compare skills
            jd_skills = set(jd_summary.get('skills', []))
            resume_skills = set(parsed_resume.get('skills', []))
            matching_skills = list(jd_skills.intersection(resume_skills))
            missing_skills = list(jd_skills - resume_skills)

            # Compare education
            jd_qualifications = set(jd_summary.get('qualifications', []))
            resume_education = set(parsed_resume.get('education', []))
            matching_education = list(jd_qualifications.intersection(resume_education))
            missing_education = list(jd_qualifications - resume_education)

            return {
                "match_score": match_score,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "matching_education": matching_education,
                "missing_education": missing_education
            }

        except Exception as e:
            self.logger.error(f"Error getting match details: {str(e)}")
            return {
                "match_score": 0.0,
                "matching_skills": [],
                "missing_skills": [],
                "matching_education": [],
                "missing_education": []
            } 