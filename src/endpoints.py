from flask import Blueprint, request, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models import DummyModel, Doctor
from webargs import fields
from webargs.flaskparser import use_args

from datetime import datetime, timedelta

home = Blueprint('/', __name__)


# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


@home.route('/')
def index():
    return {'data': 'OK'}


@home.route('/dummy_model/<id_>', methods=['GET'])
def dummy_model(id_):
    record = DummyModel.query.filter_by(id=id_).first()
    if record is not None:
        return record.json()
    else:
        return jsonify(None), HTTPStatus.NOT_FOUND


@home.route('/dummy_model', methods=['POST'])
@use_args({'value': fields.String()})
def dummy_model_create(args):
    new_record = DummyModel(value=args.get('value'))
    db.session.add(new_record)
    db.session.commit()
    return new_record.json()

# Data models
class Appointment:
    def __init__(self, doctor, start_time, end_time):
        self.doctor = doctor
        self.start_time = start_time
        self.end_time = end_time

# Helper function to create appointments
def create_seed_appointment(doctor_name, start_time_str, duration_minutes):
    start_time = datetime.fromisoformat(start_time_str)
    end_time = start_time + timedelta(minutes=duration_minutes)
    return Appointment(doctor_name, start_time, end_time)

# Seed data
# In-memory list of appointments
appointments = [
    create_seed_appointment("Strange", "2024-09-16T09:00:00", 30),
    create_seed_appointment("Strange", "2024-09-16T10:00:00", 45),
    create_seed_appointment("Strange", "2024-09-16T11:00:00", 60),
    create_seed_appointment("Who", "2024-09-16T08:00:00", 30),
    create_seed_appointment("Who", "2024-09-16T09:00:00", 30),
    create_seed_appointment("Who", "2024-09-16T10:00:00", 45),
    create_seed_appointment("Strange", "2024-09-17T14:00:00", 30),
    create_seed_appointment("Who", "2024-09-17T13:00:00", 60),
]


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

def get_first_available_appointment(doctor, after_time):
    current_time = after_time.replace(minute=0, second=0, microsecond=0)

    for day in range(7):
        current_time = current_time + timedelta(days=1)
        if current_time.weekday() >= 5:  # Skip weekends
            continue

        for hour in range(doctor.start_hour, doctor.end_hour):
            potential_start = current_time.replace(hour=hour, minute=0)
            potential_end = potential_start + timedelta(minutes=60)

            if not has_conflict(doctor.name, potential_start, potential_end) and is_within_working_hours(doctor, potential_start, potential_end):
                return potential_start

    return None

@home.route('/appointments', methods=['POST'])
@use_args({'doctorName': fields.String(), 'startTime': fields.String(), 'durationMinutes': fields.Integer()})
def create_appointment(args):
    data = request.json
    doctor_name = args.get("doctorName")
    start_time = datetime.fromisoformat(args.get("startTime"))
    duration_minutes = args.get("durationMinutes")

    # Validate doctor
    doctor = Doctor.query.filter_by(name=doctor_name).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor name"}), 400

    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Check working hours and conflicts
    if not is_within_working_hours(doctor, start_time, end_time):
        return jsonify({"error": "Appointment outside working hours"}), 400
    if has_conflict(doctor_name, start_time, end_time):
        return jsonify({"error": "Appointment conflicts with an existing one"}), 409

    # Create and store appointment
    appointment = Appointment(doctor_name, start_time, end_time)
    appointments.append(appointment)

    return jsonify({
        "doctor": doctor_name,
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat()
    }), 201


@home.route('/appointments', methods=['GET'])
def get_appointments():
    doctor_name = request.args.get("doctorName")
    start_time = datetime.fromisoformat(request.args.get("startTime"))
    end_time = datetime.fromisoformat(request.args.get("endTime"))

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor name"}), 400

    # Filter appointments
    doctor_appointments = [
        appt for appt in appointments
        if appt.doctor == doctor_name and
        appt.start_time >= start_time and appt.end_time <= end_time
    ]

    return jsonify([
        {
            "doctor": appt.doctor,
            "startTime": appt.start_time.isoformat(),
            "endTime": appt.end_time.isoformat()
        }
        for appt in doctor_appointments
    ])


# TODO: handle improperly formatted arguments (afterTime)
@home.route('/appointments/first-available', methods=['GET'])
def get_first_available():
    doctor_name = request.args.get("doctorName")
    after_time = datetime.fromisoformat(request.args.get("afterTime"))

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor name"}), 400

    first_available = get_first_available_appointment(doctor, after_time)
    if first_available:
        return jsonify({
            "doctor": doctor_name,
            "startTime": first_available.isoformat()
        })
    else:
        return jsonify({"error": "No available appointments"}), 404
