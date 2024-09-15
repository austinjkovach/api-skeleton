from datetime import datetime, timedelta
from src.models import AppointmentModel
from src.constants import MAX_APPOINTMENT_DURATION_MINUTES

def format_12hr(hour):
    return datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M%p")

def is_within_working_hours(doctor, start_time, end_time):
    start_hour = start_time.hour
    end_hour = end_time.hour
    day_of_week = start_time.weekday()  # Monday is 0, Sunday is 6

    # Check if within working hours (M-F)
    return (
        day_of_week >= 0 and day_of_week <= 4 and
        start_hour >= doctor.start_hour and end_hour <= doctor.end_hour
    )

def has_conflict(doctor, start_time, end_time):
    return any(
        appt.doctor.id == doctor.id and (
            (start_time >= appt.start_time and start_time < appt.end_time) or
            (end_time > appt.start_time and end_time <= appt.end_time) or
            (start_time <= appt.start_time and end_time >= appt.end_time)
        )
        for appt in doctor.appointments
    )

def get_first_available_appointment(doctor, after_time, duration_minutes):
    if duration_minutes > MAX_APPOINTMENT_DURATION_MINUTES:
      return None
    current_time = after_time.replace(second=0, microsecond=0)
    duration_delta = timedelta(minutes=duration_minutes)

    # Get all of the doctor's appointments sorted by start_time
    appointments = AppointmentModel.query.filter_by(doctor_id=doctor.id).order_by(AppointmentModel.start_time).all()

    # first start time to check is either doctor's opening hour of the day,
    # or the after_time from the patient, whichever is later
    doctor_start_time = current_time.replace(hour=doctor.start_hour, minute=0)
    potential_start = max(current_time, doctor_start_time)
    potential_end = potential_start + duration_delta

    i = 0
    while i < len(appointments):
      appointment = appointments[i]

      # Skip past any appointments that ended before our potential start
      if potential_start >= appointment.end_time:
        while potential_start >= appointment.end_time:
          i += 1
        continue

      # Skip weekends
      if potential_start.weekday() >= 5:
          potential_start = potential_start + timedelta(days=1)
          potential_start = potential_start.replace(hour=doctor.start_hour, minute=0)
          potential_end = potential_start + duration_delta
          continue

      # If we would end after closing, skip forward to opening of the next day
      end_hour = potential_start.replace(hour=doctor.end_hour, minute=0)
      if potential_end >= end_hour:
          potential_start = potential_start + timedelta(days=1)
          potential_start = potential_start.replace(hour=doctor.start_hour, minute=0)
          potential_end = potential_start + duration_delta
          continue

      # If next appointment start time is after our end time
      # (aka does not conflict), we can return the potential appointment.
      # Otherwise, the earliest we could schedule is the end of the next appointment
      if appointment.end_time < potential_start:
        return AppointmentModel(start_time=potential_start, end_time=potential_end, doctor_id=doctor.id)
      else:
        potential_start = appointment.end_time
        potential_end = potential_start + duration_delta
        i += 1


    # If we made it here, all intervals were conflicts.
    # Check if end_times are valid

    # Skip weekends
    while potential_start.weekday() >= 5:
        potential_start = potential_start + timedelta(days=1)
        potential_start = potential_start.replace(hour=doctor.start_hour, minute=0)
        potential_end = potential_start + duration_delta

    # If we would end after closing, skip forward to opening of the next day
    end_hour = potential_start.replace(hour=doctor.end_hour, minute=0)
    print('ajk potential end', potential_end)
    print('ajk end_hour', end_hour)
    if potential_end >= end_hour:
        potential_start = potential_start + timedelta(days=1)
        potential_start = potential_start.replace(hour=doctor.start_hour, minute=0)
        potential_end = potential_start + duration_delta

    return AppointmentModel(start_time=potential_start, end_time=potential_end, doctor_id=doctor.id)
