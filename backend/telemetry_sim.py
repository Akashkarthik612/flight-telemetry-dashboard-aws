import random
import time
import json

def generate_telemetry():
    """Simulates flight sensor data."""
    return {
        "altitude": round(random.uniform(3000, 12000), 2),   # in meters
        "speed": round(random.uniform(200, 900), 2),         # in km/h
        "temperature": round(random.uniform(-60, 40), 2)     # in Celsius
    }

if __name__ == "__main__":
    while True:
        data = generate_telemetry()
        print(json.dumps(data))
        time.sleep(2)
