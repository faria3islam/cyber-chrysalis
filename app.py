# importing core Flask modules
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # get config variables from .env file

# creating an instance of Flask as our app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sample_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# creating database connection variable
db = SQLAlchemy(app)

# create model for task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(256), nullable=False)

# home page
@app.get('/')
def home_page():
    return render_template('home.html')

# tracker page
@app.get('/tracker')
def tracker_page():
    return render_template('tracker.html')

# tracker form submission
@app.route('/tracker', methods=['POST'])
def submit():
    mood = request.form.get('mood')
    start_sleep = request.form.get('start_sleep')
    end_sleep = request.form.get('end_sleep')
    start_work = request.form.get('start_work')
    end_work = request.form.get('end_work')
    return redirect(url_for('suggestion_page', mood=mood, start_sleep=start_sleep, end_sleep=end_sleep, start_work=start_work, end_work=end_work))

# add schedule page
@app.get('/schedule')
def schedule_page():
    tasks = Task.query.all()
    return render_template('schedule.html', tasks=tasks)

# this route is called when the form is submitted on the schedule page
@app.post('/schedule')
def schedule_form():
    name = request.form.get('name')
    task = Task(task=name)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('schedule_page'))

# delete item
@app.get('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('schedule_page'))

# suggestion page
@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion_page():
    mood = request.args.get('mood')
    start_sleep = request.args.get('start_sleep')
    end_sleep = request.args.get('end_sleep')
    start_work = request.args.get('start_work')
    end_work = request.args.get('end_work')

    # Handle missing form data
    if not all([mood, start_sleep, end_sleep, start_work, end_work]):
        return "Missing form data. Please fill out the form completely."

    start_sleep = datetime.strptime(start_sleep, '%H:%M')
    end_sleep = datetime.strptime(end_sleep, '%H:%M')
    start_work = datetime.strptime(start_work, '%H:%M')
    end_work = datetime.strptime(end_work, '%H:%M')

    suggestions = []
    if any(option in mood for option in ['one', 'two', 'three', 'four', 'five', 'six']):
        suggestions.append('Start small, each step forward is victory!')
    if any(option in mood for option in ['seven', 'eight', 'nine', 'ten']):
        suggestions.append('Embrace challenges! Keep going!')

    study_times = []
    if end_sleep < start_work:
        study_times.append(f'Study from {end_sleep.strftime("%H:%M")} to {start_work.strftime("%H:%M")}')
    if end_work < start_sleep:
        study_times.append(f'Study from {end_work.strftime("%H:%M")} to {start_sleep.strftime("%H:%M")}')

    return render_template('suggestion.html', suggestions=suggestions, study_times=study_times)

# running the site
if __name__=='__main__':
    # creating db if it doesn't exist
    if not os.path.exists('instance/site.db'):
        print("Database not found, creating...")
        with app.app_context():
            db.create_all()
    PORT = os.environ.get("PORT", "5000")
    app.run(debug=True, port=PORT)