from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

nlp = spacy.load('en_core_web_sm')

def calculate_similarity(job_desc, resume_text):
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([job_desc, resume_text])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)

def extract_keywords(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]

def match_skills(job_skills, resume_skills):
    matched = set(job_skills) & set(resume_skills)
    return {
        'matched': list(matched),
        'missing': list(set(job_skills) - matched),
        'extra': list(set(resume_skills) - matched)
    }