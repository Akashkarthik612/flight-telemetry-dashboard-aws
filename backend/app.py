# backend/app.py
import os
import random
import threading
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import SessionLocal, Telemetry, Base, engine

app = FastAPI(title="Flight Telemetry Simulator")

# Allow frontend to call (for local dev). Be strict in production.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Fleet of 50 flights
flights = [{"flight_id": f"FL{100+i}", "flight_name": f"Airbus-{i+1}"} for i in range(50)]

# In-memory latest snapshot for fast API reads
latest_data = {}

def generate_telemetry_for_flight(flight):
    return {
        "flight_id": flight["flight_id"],
        "flight_name": flight["flight_name"],
        "altitude": round(random.uniform(3000, 12000), 2),
        "speed": round(random.uniform(200, 900), 2),
        "temperature": round(random.uniform(-60, 40), 2),
        "timestamp": datetime.utcnow()
    }

def simulator_loop():
    """
    Background loop: every N seconds, generate telemetry for all flights,
    persist to DB and update in-memory latest_data dict.
    """
    while True:
        db = SessionLocal()
        try:
            # Batch-insert telemetry for all flights
            for flight in flights:
                t = generate_telemetry_for_flight(flight)
                rec = Telemetry(
                    flight_id=t["flight_id"],
                    flight_name=t["flight_name"],
                    altitude=t["altitude"],
                    speed=t["speed"],
                    temperature=t["temperature"],
                    timestamp=t["timestamp"]
                )
                db.add(rec)
            db.commit()

            # Refresh latest_data for each flight (simple approach)
            for flight in flights:
                latest = db.query(Telemetry).filter(Telemetry.flight_id == flight["flight_id"])\
                         .order_by(Telemetry.timestamp.desc()).first()
                if latest:
                    latest_data[flight["flight_id"]] = {
                        "flight_id": latest.flight_id,
                        "flight_name": latest.flight_name,
                        "altitude": latest.altitude,
                        "speed": latest.speed,
                        "temperature": latest.temperature,
                        "timestamp": latest.timestamp.isoformat()
                    }
        except Exception as e:
            print("Simulator error:", e)
            db.rollback()
        finally:
            db.close()

        # pause before next round
        time.sleep(2)  # adjust frequency as desired

@app.on_event("startup")
def startup_event():
    # ensure table exists (if DB created)
    Base.metadata.create_all(bind=engine)
    # start background simulator thread
    thread = threading.Thread(target=simulator_loop, daemon=True)
    thread.start()

@app.get("/telemetry/latest")
def get_latest():
    # Return list of latest telemetry snapshots
    return list(latest_data.values())

@app.get("/telemetry/history/{flight_id}")
def get_history(flight_id: str, limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.query(Telemetry).filter(Telemetry.flight_id == flight_id)\
               .order_by(Telemetry.timestamp.desc()).limit(limit).all()
        return [
            {
                "flight_id": r.flight_id,
                "altitude": r.altitude,
                "speed": r.speed,
                "temperature": r.temperature,
                "timestamp": r.timestamp.isoformat()
            } for r in rows
        ]
    finally:
        db.close()
