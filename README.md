# CEMA-HealthSync solutions

This is a simple health information system to manage clients and health programs.

It allows medics to crete health programs like TB,MALARIA & HIV,regiter new clients,
enroll them to programs ,search for clients ,and view profiles of the enrolled clients.Client profiles can also be accesed via an api for intergration with existing systems

![view registered client details](https://github.com/Wuodmadam/CEMA-/blob/master/Screenshot%202025-04-25%20222505.png) 

# Installation

WINDOWS 

Ensure python is installed in your device and create a virtual environment

'python -m venv projectname'

Install flask library in the venv

'pip install flask'

install  Flask -SQLAlchemy for the DB 

'pip install Flask -SQLAlchemy'

clone the repo and run on a localhost server preferablly port 5000.

run the app.py then follow the link.Her is the code 
<pre>'''python
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

#jsonify - interprets python lists and dictionaries to JSON
#request - to access incoming data i.e forms 
#os -to track filepaths i.e databases(sqlite)


app = Flask(__name__) #creating an instance of the flask application
basedir = os.path.abspath(os.path.dirname(__file__)) #script path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'health.db') #DB configuration,puts the health db in the same location as script
db = SQLAlchemy(app) # links db to the flass application

# MY DATABASES

#nullable = false,means must not be empty
#unique = true ,no duplicate values

class Program(db.Model): #details of the program i.e malaria,HIV
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Client(db.Model): #Entry of clients details
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20))
    contact_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments = db.relationship('Enrollment', backref='client', lazy=True)#A client may be enrolled to multiple programs

class Enrollment(db.Model): #client registration table
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    program = db.relationship('Program', backref='enrollments') #Multiple enrollments to a single program

# Creaation of all the actual tables
with app.app_context():
    db.create_all()
    
#Route to render my html for frontend/visual
@app.route('/')
def index():
    return render_template('index.html')


# MY API

@app.route('/api/programs', methods=['POST']) # creation of programa and return status
def create_program():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Program name is required'}), 400
    
    program = Program(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(program)
    db.session.commit()
    return jsonify({
        'id': program.id,
        'name': program.name,
        'description': program.description,
        'created_at': program.created_at.isoformat()
    }), 201

@app.route('/api/clients', methods=['POST']) # add client and return status
def register_client():
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'date_of_birth']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=dob,
        gender=data.get('gender', ''),
        contact_number=data.get('contact_number', '')
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'date_of_birth': client.date_of_birth.isoformat(),
        'gender': client.gender,
        'contact_number': client.contact_number,
        'created_at': client.created_at.isoformat()
    }), 201

@app.route('/api/enrollments', methods=['POST']) # Enroll a client to a program
def enroll_client():
    data = request.get_json()
    if not data or not data.get('client_id') or not data.get('program_id'):
        return jsonify({'error': 'Client ID and Program ID are required'}), 400
    
    client = Client.query.get(data['client_id'])
    program = Program.query.get(data['program_id'])
    
    if not client or not program:
        return jsonify({'error': 'Client or Program not found'}), 404
    
    enrollment = Enrollment(
        client_id=data['client_id'],
        program_id=data['program_id']
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({
        'id': enrollment.id,
        'client_id': enrollment.client_id,
        'program_id': enrollment.program_id,
        'enrollment_date': enrollment.enrollment_date.isoformat()
    }), 201

@app.route('/api/clients/search', methods=['GET']) #lookup/search for a client using name or contact
def search_clients():
    query = request.args.get('q', '')
    clients = Client.query.filter(
        (Client.first_name.ilike(f'%{query}%')) |
        (Client.last_name.ilike(f'%{query}%')) |
        (Client.contact_number.ilike(f'%{query}%'))
    ).all()
    
    return jsonify([{
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'date_of_birth': client.date_of_birth.isoformat(),
        'gender': client.gender,
        'contact_number': client.contact_number
    } for client in clients])

@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client_profile(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    enrollments = [{
        'program_id': e.program.id,
        'program_name': e.program.name,
        'enrollment_date': e.enrollment_date.isoformat()
    } for e in client.enrollments]
    
    return jsonify({
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'date_of_birth': client.date_of_birth.isoformat(),
        'gender': client.gender,
        'contact_number': client.contact_number,
        'created_at': client.created_at.isoformat(),
        'enrollments': enrollments
    })

if __name__ == '__main__':
    app.run(debug=True)'''</pre>



