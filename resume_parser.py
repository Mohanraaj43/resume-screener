import re
import spacy
from PyPDF2 import PdfReader
from docx import Document

nlp = spacy.load('en_core_web_sm')

def extract_text(filepath, extension):
    if extension == 'pdf':
        reader = PdfReader(filepath)
        text = " ".join(page.extract_text() for page in reader.pages)
    elif extension == 'docx':
        doc = Document(filepath)
        text = " ".join(para.text for para in doc.paragraphs)
    else:  # txt
        with open(filepath, 'r') as f:
            text = f.read()
    return text

def parse_resume(text):
    doc = nlp(text)
    
    # Extract entities
    skills = []
    experiences = []
    education = []
    
    for ent in doc.ents:
        if ent.label_ == 'SKILL':
            skills.append(ent.text)
        elif ent.label_ == 'ORG' and 'experience' in ent.sent.text.lower():
            experiences.append(ent.text)
        elif ent.label_ == 'ORG' and 'education' in ent.sent.text.lower():
            education.append(ent.text)
    
    # Extract phone and email
    phone = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    
    return {
        'skills': list(set(skills)),
        'experience': list(set(experiences)),
        'education': list(set(education)),
        'contact': {
            'phone': phone.group(0) if phone else None,
            'email': email.group(0) if email else None
        }
    }