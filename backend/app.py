from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/telemetry/latest")
def get_latest_telemetry():
    data = {
        "altitude": round(random.uniform(3000, 12000), 2),
        "speed": round(random.uniform(200, 900), 2),
        "temperature": round(random.uniform(-60, 40), 2)
    }
    return data
