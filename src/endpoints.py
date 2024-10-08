from flask import Blueprint, request, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models.doctor import DoctorModel
from src.models.appointment import AppointmentModel
from src.helpers import is_within_working_hours, has_conflict, get_next_available_appointment
from src.constants import MAX_APPOINTMENT_DURATION_MINUTES

from webargs import fields
from webargs.flaskparser import use_args

from datetime import datetime, timedelta

appointments_bp = Blueprint('/appointments', __name__)


# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


@appointments_bp.route('/appointments', methods=['POST'])
@use_args({'doctor_id': fields.String(), 'start_time': fields.String(), 'end_time': fields.String()})
def create_appointment(args):
    data = request.json
    doctor_id = args.get("doctor_id")
    start_time = datetime.fromisoformat(args.get("start_time"))
    end_time = datetime.fromisoformat(args.get("end_time"))
    duration_minutes = args.get("durationMinutes")

    # Validate doctor
    doctor = DoctorModel.query.filter_by(id=doctor_id).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor id"}), 400

    # Check working hours and conflicts
    if not is_within_working_hours(doctor, start_time, end_time):
        return jsonify({"error": "Appointment outside working hours"}), 400
    if has_conflict(doctor, start_time, end_time):
        return jsonify({"error": "Appointment conflicts with an existing one"}), 409

    # Create and store appointment
    appointment = AppointmentModel(doctor_id=doctor_id, start_time=start_time, end_time=end_time)
    db.session.add(appointment)
    db.session.commit()

    return appointment.json(), 201


@appointments_bp.route('/appointments', methods=['GET'])
def get_appointments():
    doctor_id = request.args.get("doctor_id")
    start_time = datetime.fromisoformat(request.args.get("start_time"))
    end_time = datetime.fromisoformat(request.args.get("end_time"))

    doctor = DoctorModel.query.filter_by(id=doctor_id).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor name"}), 400

    # Query appointments for the specified doctor within the given time range
    doctor_appointments = AppointmentModel.query.filter(
        AppointmentModel.doctor_id == doctor.id,
        AppointmentModel.start_time >= start_time,
        AppointmentModel.end_time <= end_time
    ).order_by(AppointmentModel.start_time).all()

    return jsonify([{
        'id': appt.id,
        'start_time': appt.start_time,
        'end_time': appt.end_time,
        'doctor': {
          'id': appt.doctor.id,
          'name': appt.doctor.name
        }
    } for appt in doctor_appointments])

@appointments_bp.route('/appointments/next-available', methods=['GET'])
def get_next_available():
    doctor_id = request.args.get("doctor_id")
    after_time = datetime.fromisoformat(request.args.get("after"))
    duration_minutes = int(request.args.get("duration_minutes"))

    if duration_minutes > MAX_APPOINTMENT_DURATION_MINUTES:
        return jsonify({"error": "Cannot book appointment longer than 2 hours"}), 400

    doctor = DoctorModel.query.filter_by(id=doctor_id).first()
    if not doctor:
        return jsonify({"error": "Invalid doctor id"}), 400

    next_available = get_next_available_appointment(doctor, after_time, duration_minutes)
    if next_available:
        return jsonify({
          'start_time': next_available.start_time.isoformat(),
          'end_time': next_available.end_time.isoformat(),
          'doctor': {
            'id': doctor.id,
            'name': doctor.name
          }
        })
    else:
        return jsonify({"error": "No available appointments"}), 404
