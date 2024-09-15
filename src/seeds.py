# from src.extensions import db
from datetime import datetime, timedelta
from src.models import DoctorModel, AppointmentModel
from src.extensions import db

def seed_database(app):
  with app.app_context():
    seed_doctors()
    seed_appointments()


def seed_doctors():
      print('Seeding Doctors...')
      # Create Doctor instances
      strange = DoctorModel(name="Strange", start_hour=9, end_hour=17)
      who = DoctorModel(name="Who", start_hour=8, end_hour=16)

      # Add to the session
      db.session.add(strange)
      db.session.add(who)
      db.session.commit()

      doctors = DoctorModel.query.all()

      for doctor in doctors:
          fstart = format_12hr(doctor.start_hour)
          fend = format_12hr(doctor.end_hour)
          print('\tDoctor %s | %s-%s M-F' % (doctor.name, fstart, fend))

      print('Seeded %s Doctors:' % len(doctors))
      print('\n\n')

def format_12hr(hour):
    return datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M%p")

def create_seed_appointment(appt):

    start_time = datetime.fromisoformat(appt["start_time"])
    end_time = start_time + timedelta(minutes=appt["duration"])

    appointment = AppointmentModel(doctor_id=appt["doctor"].id, start_time=start_time, end_time=end_time)

    print('\t', appointment)
    db.session.add(appointment)
    db.session.commit()

def seed_appointments():
    print('Seeding Appointments...')

    strange = DoctorModel.query.filter_by(name="Strange").first()
    who = DoctorModel.query.filter_by(name="Who").first()

    appointments = [
      { "doctor": strange, "start_time": "2024-09-16T09:00:00", "duration": 30},
      { "doctor": strange, "start_time": "2024-09-16T10:00:00", "duration": 45},
      { "doctor": strange, "start_time": "2024-09-16T11:00:00", "duration": 60},
      { "doctor": strange, "start_time": "2024-09-17T14:00:00", "duration": 30},
      { "doctor": who, "start_time": "2024-09-16T08:00:00", "duration": 30},
      { "doctor": who, "start_time": "2024-09-16T09:00:00", "duration": 30},
      { "doctor": who, "start_time": "2024-09-16T10:00:00", "duration": 45},
      { "doctor": who, "start_time": "2024-09-17T13:00:00", "duration": 60}
    ]

    for appt in appointments:
      create_seed_appointment(appt)

    print('Seeded %s appointments'  % len(appointments))
    print('\n')

# if __name__ == "__main__":
#   seed_database()