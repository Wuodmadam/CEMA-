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