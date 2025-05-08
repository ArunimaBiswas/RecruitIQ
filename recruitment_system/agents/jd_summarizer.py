import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import logging

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class JDSummarizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english')) - {'not', 'and', 'or'}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_text(self, text):
        """Process text using the existing preprocessing logic"""
        if not isinstance(text, str):
            text = '' if text is None else str(text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s\-\+]', '', text)
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    def extract_skills(self, text):
        """Extract technical skills from job description"""
        common_skills = {
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data science', 'react', 'node.js',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        }
        processed_text = self.process_text(text)
        tokens = set(word_tokenize(processed_text))
        found_skills = tokens.intersection(common_skills)
        return list(found_skills)

    def extract_qualifications(self, text):
        """Extract educational qualifications"""
        qualifications = []
        if 'bachelor' in text.lower():
            qualifications.append("Bachelor's Degree")
        if 'master' in text.lower():
            qualifications.append("Master's Degree")
        if 'phd' in text.lower() or 'doctorate' in text.lower():
            qualifications.append("PhD")
        return qualifications

    def extract_experience(self, text):
        """Extract experience requirements"""
        experience_patterns = [
            r'(\d+)[\+]?\s*(?:year|yr)s?',
            r'(\d+)[\+]?\s*(?:year|yr)s?\s*of\s*experience',
            r'experience\s*of\s*(\d+)[\+]?\s*(?:year|yr)s?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return f"{matches[0]}+ years"
        return "Not specified"

    def summarize(self, jd_text):
        """Generate a comprehensive summary of the job description"""
        try:
            summary = {
                "skills": self.extract_skills(jd_text),
                "qualifications": self.extract_qualifications(jd_text),
                "experience": self.extract_experience(jd_text),
                "processed_text": self.process_text(jd_text)
            }
            return json.dumps(summary)
        except Exception as e:
            self.logger.error(f"Error in JD summarization: {str(e)}")
            return json.dumps({
                "skills": [],
                "qualifications": [],
                "experience": "Not specified",
                "processed_text": self.process_text(jd_text)
            }) 