import os
import json
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

class Scheduler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Google OAuth"""
        try:
            # Check if we have stored credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)

            # If credentials are not valid or don't exist, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True

        except Exception as e:
            self.logger.error(f"Error in Google authentication: {str(e)}")
            return False

    def generate_interview_slots(self, start_date=None, days=5):
        """Generate available interview slots"""
        if start_date is None:
            start_date = datetime.now()
        
        slots = []
        current_date = start_date
        
        for _ in range(days):
            # Generate slots for each day (9 AM to 5 PM, 1-hour slots)
            for hour in range(9, 17):
                slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slots.append(slot_time)
            current_date += timedelta(days=1)
        
        return slots

    def send_interview_invitation(self, candidate_email, interview_time, job_title):
        """Send interview invitation email using Gmail API"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False

            # Create email message
            message = {
                'raw': self._create_message(
                    to=candidate_email,
                    subject=f"Interview Invitation - {job_title}",
                    body=f"""
                    Dear Candidate,

                    You are invited for an interview for the position of {job_title}.
                    
                    Interview Details:
                    Date and Time: {interview_time.strftime('%B %d, %Y at %I:%M %p')}
                    
                    Please confirm your attendance by replying to this email.
                    
                    Best regards,
                    Recruitment Team
                    """
                )
            }

            # Send email
            self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending interview invitation: {str(e)}")
            return False

    def _create_message(self, to, subject, body):
        """Create email message in base64url format"""
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        return base64.urlsafe_b64encode(message.as_bytes()).decode()

    def schedule(self, application_id, candidate_email, job_title):
        """Schedule an interview and send invitation"""
        try:
            # Generate interview slots
            slots = self.generate_interview_slots()
            
            # For now, just pick the first available slot
            # In a real system, you'd want to check availability and preferences
            interview_time = slots[0]
            
            # Send invitation
            if self.send_interview_invitation(candidate_email, interview_time, job_title):
                return {
                    "interview_time": interview_time.isoformat(),
                    "status": "scheduled"
                }
            else:
                return {
                    "interview_time": None,
                    "status": "failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error scheduling interview: {str(e)}")
            return {
                "interview_time": None,
                "status": "error"
            } 