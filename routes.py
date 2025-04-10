from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Job, Resume
from app.utils.resume_parser import extract_text, parse_resume
from app.utils.matcher import calculate_similarity, match_skills
from config import Config

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle job posting
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        
        job = Job(title=title, description=description, requirements=requirements)
        db.session.add(job)
        db.session.commit()
        
        return redirect(url_for('main.job_details', job_id=job.id))
    
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

@bp.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        # Handle resume upload
        if 'resume' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Process resume
            extension = filename.rsplit('.', 1)[1].lower()
            text = extract_text(filepath, extension)
            parsed_data = parse_resume(text)
            
            # Calculate match
            similarity = calculate_similarity(job.description + ' ' + job.requirements, text)
            skill_match = match_skills(
                extract_keywords(job.requirements),
                parsed_data['skills']
            )
            
            # Save to database
            resume = Resume(
                filename=filename,
                filepath=filepath,
                score=similarity,
                matched_skills=', '.join(skill_match['matched']),
                job_id=job.id
            )
            db.session.add(resume)
            db.session.commit()
            
            return redirect(url_for('main.job_details', job_id=job.id))
    
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.score.desc()).all()
    return render_template('job.html', job=job, resumes=resumes)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS