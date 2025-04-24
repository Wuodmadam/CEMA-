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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))

class Client(db.Model): #Entry of clients details
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20))
    contact_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    enrollments = db.relationship('Enrollment', backref='client', lazy=True)#A client may be enrolled to multiple programs

class Enrollment(db.Model): #client registration table
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    program = db.relationship('Program', backref='enrollments') #Multiple enrollments to a single program

