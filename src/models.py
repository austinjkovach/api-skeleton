from src.extensions import db
from flask import jsonify


class DummyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String, nullable=False)

    def json(self) -> str:
        """
        :return: Serializes this object to JSON
        """
        return jsonify({'id': self.id, 'value': self.value})

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Doctor {self.name}>'

    def json(self):
        return jsonify({
            'id': self.id,
            'name': self.name,
            'start_hour': self.start_hour,
            'end_hour': self.end_hour
        })

# class Doctor:
#     def __init__(self, name, start_hour, end_hour):
#         self.name = name
#         self.start_hour = start_hour
#         self.end_hour = end_hour

# class Appointment:
#     def __init__(self, doctor, start_time, end_time):
#         self.doctor = doctor
#         self.start_time = start_time
#         self.end_time = end_time


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_name = db.Column(db.String, db.ForeignKey('doctor.name'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return f'<Appointment {self.doctor.name} from {self.start_time} to {self.end_time}>'

    def json(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }