from src.extensions import db
from flask import jsonify

class DoctorModel(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)

    appointments = db.relationship('AppointmentModel', back_populates="doctor")

    def __repr__(self):
        return f'<DoctorModel {self.name}>'

    def json(self):
        return jsonify({
            'id': self.id,
            'name': self.name,
            'start_hour': self.start_hour,
            'end_hour': self.end_hour
        })