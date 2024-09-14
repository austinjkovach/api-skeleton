# from src.extensions import db
from datetime import datetime
from src.models import Doctor

def seed_database(app, db):
  with app.app_context():
    seed_doctors(db)

def seed_appointments(db):
  return None

def seed_doctors(db):
      # Create Doctor instances
      strange = Doctor(name="Strange", start_hour=9, end_hour=17)
      who = Doctor(name="Who", start_hour=8, end_hour=16)

      # Add to the session
      db.session.add(strange)
      db.session.add(who)

      # Commit the session to save to the database
      db.session.commit()

      # Verify by querying
      doctors = Doctor.query.all()
      print('Seeding Doctors...')

      for doctor in doctors:
          fstart = format_12hr(doctor.start_hour)
          fend = format_12hr(doctor.end_hour)
          print('\tDoctor %s | %s-%s M-F' % (doctor.name, fstart, fend))

      print('Seeded %s Doctors:' % len(doctors))
      print('\n\n')

def format_12hr(hour):
    return datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M%p")
# if __name__ == "__main__":
#   seed_database()