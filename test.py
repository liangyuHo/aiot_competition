import requests
import random

while True:
    data = {
        'HR': random.randint(60, 100),
        'SpO2': random.randint(90, 100),
        'RR': random.randint(12, 20),
        'R': random.uniform(0, 10),
        'activity': random.randint(0, 100),
        'motion': random.randint(0, 100),
        'hrconf': random.uniform(0, 1),
        'rrconf': random.uniform(0, 1),
        'wspo2conf': random.uniform(0, 1)
    }

    print(data)
    response = requests.post("http://localhost:8000/health_predict/", json=data)