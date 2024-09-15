from src.extensions import db
from flask import jsonify

class AppointmentModel(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    doctor = db.relationship('DoctorModel', back_populates='appointments')

    def __repr__(self):
        if not self.doctor:
          return f'<Appointment {self.doctor_id} from {self.start_time} to {self.end_time}>'
        else:
          return f'<Appointment {self.doctor.name} from {self.start_time} to {self.end_time}>'


    def json(self):
        return jsonify({
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'doctor': {
              'id': self.doctor.id,
              'name': self.doctor.name
            }
        })