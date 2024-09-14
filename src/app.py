from flask import Flask, jsonify
from src.extensions import db
from src.endpoints import home



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    # We are doing a create all here to set up all the tables. Because we are using an in memory sqllite db, each
    # restart wipes the db clean, but does have the advantage of not having to worry about schema migrations.
    with app.app_context():
        db.create_all()
    app.register_blueprint(home)
    return app



# Data models
class Doctor:
    def __init__(self, name, start_hour, end_hour):
        self.name = name
        self.start_hour = start_hour
        self.end_hour = end_hour

class Appointment:
    def __init__(self, doctor, start_time, end_time):
        self.doctor = doctor
        self.start_time = start_time
        self.end_time = end_time

# Define doctors and their working hours
doctors = {
    "Strange": Doctor("Strange", 9, 17),
    "Who": Doctor("Who", 8, 16)
}

# In-memory list of appointments
appointments = []

# Helper functions
def is_within_working_hours(doctor, start_time, end_time):
    start_hour = start_time.hour
    end_hour = end_time.hour
    day_of_week = start_time.weekday()  # Monday is 0, Sunday is 6

    # Check if within working hours (M-F)
    return (
        day_of_week >= 0 and day_of_week <= 4 and
        start_hour >= doctor.start_hour and end_hour <= doctor.end_hour
    )

def has_conflict(doctor_name, start_time, end_time):
    return any(
        appt.doctor == doctor_name and (
            (start_time >= appt.start_time and start_time < appt.end_time) or
            (end_time > appt.start_time and end_time <= appt.end_time) or
            (start_time <= appt.start_time and end_time >= appt.end_time)
        )
        for appt in appointments
    )
