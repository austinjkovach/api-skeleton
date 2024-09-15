from http import HTTPStatus
from datetime import datetime

def test_create_appointment(client, db_session):
    # Post a valid appointment
    response = client.post('/appointments', json={
        'doctor_id': '1',
        'start_time': '2024-09-16T09:30:00',
        'end_time': '2024-09-16T10:00:00'
    })

    # Assert successful creation
    assert response.status_code == HTTPStatus.CREATED
    data = response.json
    assert 'id' in data
    assert data['start_time'] == '2024-09-16T09:30:00'
    assert data['end_time'] == '2024-09-16T10:00:00'
    assert data['doctor']['id'] == 1


def test_create_appointment_invalid_doctor(client):
    # Post an appointment with an invalid doctor ID
    response = client.post('/appointments', json={
        'doctor_id': '999',  # Invalid doctor ID
        'start_time': '2024-09-16T10:00:00',
        'end_time': '2024-09-16T10:30:00'
    })

    # Assert bad request error
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json['error'] == "Invalid doctor id"


def test_create_appointment_conflict(client, db_session):
    # Assuming doctor already has an appointment at this time based on seed files
    response = client.post('/appointments', json={
        'doctor_id': '1',
        'start_time': '2024-09-16T10:00:00',
        'end_time': '2024-09-16T11:00:00'
    })

    # Assert conflict response
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json['error'] == "Appointment conflicts with an existing one"

def test_get_appointments(client, db_session):
    response = client.get('/appointments?doctor_id=1&start_time=2024-09-16T00:00:00&end_time=2024-09-16T23:59:59')

    # Assert success
    assert response.status_code == HTTPStatus.OK
    appointments = response.json
    assert isinstance(appointments, list)

    # Check the structure of the first appointment
    if len(appointments) > 0:
        first_appointment = appointments[0]
        assert 'id' in first_appointment
        assert 'start_time' in first_appointment
        assert 'end_time' in first_appointment
        assert 'doctor' in first_appointment
        assert first_appointment['doctor']['id'] == 1


def test_get_next_available_appointment(client, db_session):
    response = client.get('/appointments/next-available?doctor_id=1&after=2024-09-16T12:00:00&duration_minutes=30')

    # Assert success or 404
    assert response.status_code == HTTPStatus.OK or HTTPStatus.NOT_FOUND
    if response.status_code == HTTPStatus.OK:
        next_available = response.json
        assert 'start_time' in next_available
        assert 'end_time' in next_available
        assert 'doctor' in next_available
        assert next_available['doctor']['id'] == 1
    else:
        assert response.json['error'] == "No available appointments"

def test_get_next_available_invalid_duration(client):
    response = client.get('/appointments/next-available?doctor_id=1&after=2024-09-16T12:00:00&duration_minutes=130')

    # Assert error for exceeding maximum duration
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json['error'] == "Cannot book appointment longer than 2 hours"
