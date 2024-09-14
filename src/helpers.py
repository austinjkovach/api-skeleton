from datetime import datetime, timedelta

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