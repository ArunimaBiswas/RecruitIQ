import pdfplumber
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import logging
import os

class ResumeParserAgent:
    def __init__(self):
        self.stop_words = set(stopwords.words('english')) - {'not', 'and', 'or'}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common section headers in resumes
        self.section_headers = {
            'education': ['education', 'academic', 'qualification'],
            'experience': ['experience', 'work', 'employment', 'professional'],
            'skills': ['skills', 'technical skills', 'competencies'],
            'projects': ['projects', 'project experience']
        }

    def process_text(self, text):
        """Process text using the existing preprocessing logic"""
        if not isinstance(text, str):
            text = '' if text is None else str(text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s\-\+]', '', text)
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    def extract_sections(self, text):
        """Extract different sections from the resume"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
                
            # Check if line is a section header
            for section, headers in self.section_headers.items():
                if any(header in line for header in headers):
                    current_section = section
                    sections[section] = []
                    break
            
            if current_section and line:
                sections[current_section].append(line)
        
        return sections

    def extract_skills(self, text):
        """Extract technical skills from resume"""
        common_skills = {
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data science', 'react', 'node.js',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        }
        processed_text = self.process_text(text)
        tokens = set(word_tokenize(processed_text))
        found_skills = tokens.intersection(common_skills)
        return list(found_skills)

    def extract_education(self, sections):
        """Extract education information"""
        education = []
        if 'education' in sections:
            for line in sections['education']:
                if any(degree in line.lower() for degree in ['bachelor', 'master', 'phd', 'bs', 'ms', 'mba']):
                    education.append(line)
        return education

    def parse(self, resume_path):
        """Parse a resume PDF and extract relevant information"""
        try:
            if not os.path.exists(resume_path):
                raise FileNotFoundError(f"Resume file not found: {resume_path}")

            # Extract text from PDF
            with pdfplumber.open(resume_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''

            # Process the extracted text
            sections = self.extract_sections(text)
            processed_text = self.process_text(text)
            
            # Extract information
            parsed_data = {
                "skills": self.extract_skills(text),
                "education": self.extract_education(sections),
                "processed_text": processed_text,
                "sections": sections
            }
            
            return json.dumps(parsed_data)
            
        except Exception as e:
            self.logger.error(f"Error in resume parsing: {str(e)}")
            return json.dumps({
                "skills": [],
                "education": [],
                "processed_text": "",
                "sections": {}
            }) 