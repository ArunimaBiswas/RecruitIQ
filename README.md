# RecruitIQ

RecruitIQ is an intelligent recruitment system that leverages AI and machine learning to streamline the hiring process. The system includes resume parsing, candidate matching, and automated screening capabilities.

## Features

- Resume parsing and analysis
- AI-powered candidate matching
- Automated screening process
- Interactive dashboard
- Google Calendar integration
- Candidate database management

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Streamlit
- **AI/ML**: PyTorch, Transformers, scikit-learn
- **Database**: SQLite
- **Document Processing**: PDFPlumber
- **Google Integration**: Google Calendar API

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RecruitIQ
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
RecruitIQ/
├── recruitment_system/     # Main application directory
│   ├── app.py             # Flask application
│   ├── streamlit_app.py   # Streamlit dashboard
│   ├── models.py          # Database models
│   ├── templates/         # HTML templates
│   ├── static/           # Static files
│   └── agents/           # AI agents
├── distilbert_resume_matcher/  # Resume matching model
├── requirements.txt       # Project dependencies
└── venv/                 # Virtual environment
```

## Usage

1. Start the Flask backend:
```bash
cd recruitment_system
python app.py
```

2. Launch the Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```

## Features in Detail

### Resume Parsing
- Extracts information from PDF resumes
- Identifies key skills, experience, and education
- Standardizes resume data for analysis

### Candidate Matching
- Uses DistilBERT for semantic matching
- Compares candidate profiles with job requirements
- Provides match scores and recommendations

### Automated Screening
- Initial candidate evaluation
- Skill assessment
- Experience verification

### Dashboard
- Interactive data visualization
- Candidate tracking
- Interview scheduling
- Analytics and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Contact

[Add your contact information here]
