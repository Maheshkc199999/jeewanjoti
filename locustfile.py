from locust import HttpUser, task, between, events
from decouple import config
import json
import random
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env
BASE_URL = config("BASE_URL", default="https://jeewanjyoti-test.smart.org.np")
EMAIL = config("TEST_EMAIL", default="mkc7025@gmail.com")
PASSWORD = config("TEST_PASSWORD", default="Mecha7970@")
STATIC_JWT_TOKEN = config(
    "JWT_TOKEN",
    default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzgyNjY1LCJpYXQiOjE3NDIxOTA2NjUsImp0aSI6ImZlOTU5ZGZhNjAxNDQ1ZWRiNjIyYzgwMzE1MWU5NTUwIiwidXNlcl9pZCI6NH0.okEC2zGB0gf9iV2zQOkteD_gLI3iKOfuq2YjoRE_9cg"
)

class HealthDataUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        if STATIC_JWT_TOKEN:
            self.headers = {
                "Authorization": f"Bearer {STATIC_JWT_TOKEN}",
                "Content-Type": "application/json"
            }
        else:
            response = self.client.post(
                f"{BASE_URL}/api/token/",
                data=json.dumps({"email": EMAIL, "password": PASSWORD}),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                token = response.json()["access"]
                self.headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            else:
                logging.error(f"Failed to get token: {response.text}")
                self.environment.runner.quit()

    def random_date(self):
        return (datetime.now() + timedelta(minutes=random.randint(1, 60))).isoformat() + "Z"

    # 1. HeartRate_Data
    @task(3)
    def test_heartrate_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": self.random_date(),
                    "once_heart_value": random.randint(60, 100)
                }
                for _ in range(2)
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/HeartRate_Data/",
            data=json.dumps(payload),
            headers=self.headers,
            name="HeartRate POST"
        )

    @task(1)
    def test_heartrate_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/HeartRate_Data/",
            params=params,
            headers=self.headers,
            name="HeartRate GET"
        )

    # 2. HRV
    @task(2)
    def test_hrv_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": self.random_date(),
                    "highBP": random.randint(110, 140),
                    "lowBP": random.randint(70, 90),
                    "stress": random.randint(20, 50),
                    "heartRate": random.randint(60, 100),
                    "vascularAging": random.randint(30, 60),
                    "hrv": random.randint(40, 80)
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/HRV-data/",
            data=json.dumps(payload),
            headers=self.headers,
            name="HRV POST"
        )

    @task(1)
    def test_hrv_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/HRV-data/",
            params=params,
            headers=self.headers,
            name="HRV GET"
        )

    # 3. BloodOxygen (Spo2)
    @task(2)
    def test_spo2_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": self.random_date(),
                    "Blood_oxygen": random.randint(90, 100)
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/Spo2-data/",
            data=json.dumps(payload),
            headers=self.headers,
            name="Spo2 POST"
        )

    @task(1)
    def test_spo2_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/Spo2-data/",
            params=params,
            headers=self.headers,
            name="Spo2 GET"
        )

    # 4. activity_day_total
    @task(2)
    def test_activity_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": (datetime.now() + timedelta(days=random.randint(1, 5))).date().isoformat(),
                    "goal": random.randint(5000, 10000),
                    "distance": random.uniform(2.0, 10.0),
                    "step": random.randint(3000, 12000),
                    "exercise_time": random.randint(20, 120),
                    "calories": random.uniform(100, 500),
                    "exercise_minutes": random.randint(15, 90)
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/Day_total_activity/",
            data=json.dumps(payload),
            headers=self.headers,
            name="Activity POST"
        )

    @task(1)
    def test_activity_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/Day_total_activity/",
            params=params,
            headers=self.headers,
            name="Activity GET"
        )

    # 5. StepData
    @task(2)
    def test_steps_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": self.random_date(),
                    "detail_minter_step": random.randint(50, 200),  # Corrected from 'minter'
                    "distance": random.uniform(0.1, 1.0),
                    "calories": random.uniform(10, 50),
                    "array_steps": json.dumps([random.randint(10, 100) for _ in range(5)])
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/Steps/",
            data=json.dumps(payload),
            headers=self.headers,
            name="Steps POST"
        )

    @task(1)
    def test_steps_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/Steps/",
            params=params,
            headers=self.headers,
            name="Steps GET"
        )

    # 6. BodyTemperature
    @task(2)
    def test_temperature_post(self):
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": self.random_date(),
                    "axillaryTemperature": random.uniform(36.0, 38.0)
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/temperature_data/",
            data=json.dumps(payload),
            headers=self.headers,
            name="Temperature POST"
        )

    @task(1)
    def test_temperature_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/temperature_data/",
            params=params,
            headers=self.headers,
            name="Temperature GET"
        )

    # 7. SleepData
    @task(2)
    def test_sleep_post(self):
        start_time = self.random_date()
        end_time = (datetime.fromisoformat(start_time[:-1]) + timedelta(hours=8)).isoformat() + "Z"
        awake = random.uniform(5, 20)
        deep = random.uniform(20, 40)
        light = random.uniform(30, 50)
        medium = 100 - (awake + deep + light)  # Ensure sum = 100%
        payload = {
            "device_id": f"device{random.randint(1, 10)}",
            "values": [
                {
                    "date": start_time,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": 480.0,  # 8 hours in minutes
                    "sleep_quality_sequence": json.dumps([random.randint(1, 3) for _ in range(4)]),
                    "awake_percentage": awake,
                    "deep_sleep_percentage": deep,
                    "light_sleep_percentage": light,
                    "medium_sleep_percentage": medium
                }
            ]
        }
        self.client.post(
            f"{BASE_URL}/api/sleep-data/",
            data=json.dumps(payload),
            headers=self.headers,
            name="Sleep POST"
        )

    @task(1)
    def test_sleep_get(self):
        params = {
            "user_id": config("TEST_USER_ID", default=3, cast=int),
            "from": "2025-03-01",
            "to": "2025-03-17",
            "device_id": f"device{random.randint(1, 10)}"
        }
        self.client.get(
            f"{BASE_URL}/api/sleep-data/",
            params=params,
            headers=self.headers,
            name="Sleep GET"
        )

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, exception, **kwargs):
    if exception:
        logging.error(f"Request failed: {name} - Exception: {exception}")
    elif response.status_code >= 400:
        logging.error(f"Request failed: {name} - Status: {response.status_code} - Response: {response.text}")
    else:
        logging.info(f"Request succeeded: {name} - Status: {response.status_code}")