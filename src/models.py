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

class DoctorModel(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<DoctorModel {self.name}>'

    def json(self):
        return jsonify({
            'id': self.id,
            'name': self.name,
            'start_hour': self.start_hour,
            'end_hour': self.end_hour
        })

class AppointmentModel(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    doctor = db.relationship('DoctorModel', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        print('DOC', self.doctor)
        if not self.doctor:
          return f'<Appointment {self.doctor_id} from {self.start_time} to {self.end_time}>'
        else:
          return f'<Appointment {self.doctor.name} from {self.start_time} to {self.end_time}>'

    def json(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }