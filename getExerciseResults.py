import requests
import configparser

# Read credentials from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

username = config['credentials']['username']
password = config['credentials']['password']

# Define the login URL and patients URL
login_url = 'https://telerehab-develop.biomed.ntua.gr/api/Login'
patients_url = 'https://telerehab-develop.biomed.ntua.gr/api/PatientManagement/patients/all'

# Prepare the payload for login
login_payload = {
    "username": username,
    "password": password
}

# Function to get the weekly program for a patient by their patientId
def get_weekly_program(patient_id, token):
    # URL for retrieving the weekly program of the patient
    weekly_program_url = f'https://telerehab-develop.biomed.ntua.gr/api/PatientSchedule/weekly/latest/{patient_id}'
    
    # Prepare headers with the Authorization token
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}'  # Ensure 'Bearer' prefix is included
    }
    
    # Make the GET request to fetch the weekly program
    weekly_program_response = requests.get(weekly_program_url, headers=headers)
    
    if weekly_program_response.status_code == 200:
        weekly_program_data = weekly_program_response.json()
        print(f"Patient {patient_id} weekly program status: {weekly_program_data.get('scheduleStatus', 'No status available')}")
        
        # Process the schedule
        schedule = weekly_program_data.get('schedule', [])
        
        # Dictionary to store unique exercises (keyed by exerciseId and progression)
        unique_exercises = {}

        for exercise in schedule:
            exercise_id = exercise.get('exerciseId')
            progression = exercise.get('progression', 0)
            
            # Use (exercise_id, progression) as the key to keep only one entry per exercise
            if (exercise_id, progression) not in unique_exercises:
                unique_exercises[(exercise_id, progression)] = exercise

        # Print the filtered unique exercises
        for key, exercise in unique_exercises.items():
            exercise_name = exercise.get('exerciseName', 'Unknown')
            progression = exercise.get('progression', 0)
            performed = exercise.get('performed', False)
            week = exercise.get('weekNumber', 'Unknown')
            year = exercise.get('year', 'Unknown')
            
            print(f"Exercise: {exercise_name}, Week: {week}, Year: {year}, Progression: {progression}, Performed: {performed}")
    else:
        print(f"Failed to retrieve weekly program for patient {patient_id}, status code: {weekly_program_response.status_code}")



# Send the login request
response = requests.post(login_url, json=login_payload, headers={'accept': '*/*', 'Content-Type': 'application/json-patch+json'})

# Check if login was successful
if response.status_code == 200:
    print("Login successful!")
    token = response.json().get('message')
    
    if token:
        # Prepare headers with the Authorization token
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {token}'  # Ensure 'Bearer' prefix is included
        }
        
        # Send request to get all patients
        patients_response = requests.get(patients_url, headers=headers)
        
        if patients_response.status_code == 200:
            data = patients_response.json()
            
            # Extract and process each patientId
            patient_ids = [patient['patientId'] for patient in data]
            for patient_id in patient_ids:
                # Get the weekly program for each patient
                get_weekly_program(patient_id, token)
        else:
            print(f"Failed to retrieve patients, status code: {patients_response.status_code}")
    else:
        print("Failed to retrieve token from login response.")
else:
    print(f"Failed to login, status code: {response.status_code}")
