import asyncio
import aiohttp
import random
import json
import time
from datetime import datetime
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightSimulator:
    def __init__(self, flight_id: str, backend_url: str = "http://localhost:8000"):
        self.flight_id = flight_id
        self.backend_url = backend_url
        self.session = None
        self.running = False
        
        # Flight parameters for realistic simulation
        self.base_altitude = random.uniform(8000, 11000)
        self.base_speed = random.uniform(800, 950)
        self.altitude_trend = random.choice([-1, 0, 1])  # climbing, cruise, descending
        self.mission_time = 0
    
    def generate_realistic_telemetry(self):
        """Generate realistic flight telemetry with flight phases"""
        self.mission_time += 2  # 2 seconds per update
        
        # Altitude variations based on flight phase
        if self.mission_time < 600:  # First 10 minutes - climbing
            altitude_change = random.uniform(5, 15)
            self.base_altitude += altitude_change
        elif self.mission_time > 3600:  # After 1 hour - possible descent
            if random.random() < 0.1:  # 10% chance to start descent
                self.altitude_trend = -1
        
        if self.altitude_trend == 1:  # Climbing
            altitude = self.base_altitude + random.uniform(-100, 200)
        elif self.altitude_trend == -1:  # Descending
            altitude = max(3000, self.base_altitude - random.uniform(0, 300))
        else:  # Cruise
            altitude = self.base_altitude + random.uniform(-200, 200)
        
        # Speed variations
        speed = self.base_speed + random.uniform(-50, 50)
        
        # Temperature based on altitude (realistic atmospheric model)
        temperature = 15 - (altitude / 1000) * 6.5 + random.uniform(-5, 5)
        
        return {
            "flight_id": self.flight_id,
            "altitude": round(altitude, 2),
            "speed": round(speed, 2),
            "temperature": round(temperature, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def start_simulation(self, interval: float = 2.0, duration: int = None):
        """Start sending telemetry data"""
        self.running = True
        self.session = aiohttp.ClientSession()
        
        logger.info(f"Starting simulation for flight {self.flight_id}")
        start_time = time.time()
        
        try:
            while self.running:
                if duration and (time.time() - start_time) > duration:
                    break
                
                telemetry = self.generate_realistic_telemetry()
                
                try:
                    async with self.session.post(
                        f"{self.backend_url}/telemetry",
                        json=telemetry,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            logger.debug(f"Sent data for {self.flight_id}")
                        else:
                            logger.warning(f"Failed to send data for {self.flight_id}: {response.status}")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout sending data for {self.flight_id}")
                except Exception as e:
                    logger.error(f"Error sending data for {self.flight_id}: {e}")
                
                await asyncio.sleep(interval)
        
        finally:
            await self.session.close()
            logger.info(f"Stopped simulation for flight {self.flight_id}")
    
    async def stop_simulation(self):
        """Stop the simulation"""
        self.running = False

class LoadTestManager:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.simulators = []
        self.running = False
    
    async def start_load_test(self, num_flights: int = 10, interval: float = 2.0, 
                            ramp_up: bool = True, duration: int = None):
        """Start load test with multiple flights"""
        logger.info(f"Starting load test with {num_flights} flights")
        
        # Generate flight IDs
        flight_ids = [f"FL{str(i).zfill(3)}" for i in range(1, num_flights + 1)]
        
        # Create simulators
        self.simulators = [
            FlightSimulator(flight_id, self.backend_url) 
            for flight_id in flight_ids
        ]
        
        # Start simulations
        if ramp_up:
            # Gradual ramp-up to test auto-scaling
            for i, sim in enumerate(self.simulators):
                asyncio.create_task(sim.start_simulation(interval, duration))
                if i < len(self.simulators) - 1:
                    await asyncio.sleep(5)  # 5-second intervals between new flights
                logger.info(f"Started flight {i+1}/{num_flights}")
        else:
            # Start all at once for stress testing
            tasks = [
                asyncio.create_task(sim.start_simulation(interval, duration))
                for sim in self.simulators
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_load_test(self):
        """Stop all simulations"""
        logger.info("Stopping load test...")
        for sim in self.simulators:
            await sim.stop_simulation()

async def main():
    parser = argparse.ArgumentParser(description="Flight Telemetry Simulator")
    parser.add_argument("--flights", type=int, default=10, help="Number of flights to simulate")
    parser.add_argument("--interval", type=float, default=2.0, help="Telemetry interval in seconds")
    parser.add_argument("--duration", type=int, help="Test duration in seconds")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--ramp-up", action="store_true", help="Gradual ramp-up of flights")
    parser.add_argument("--stress-test", action="store_true", help="High-frequency stress test")
    
    args = parser.parse_args()
    
    if args.stress_test:
        args.flights = 50
        args.interval = 0.5
        logger.info("Starting stress test mode")
    
    load_manager = LoadTestManager(args.backend)
    
    try:
        await load_manager.start_load_test(
            num_flights=args.flights,
            interval=args.interval,
            ramp_up=args.ramp_up,
            duration=args.duration
        )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await load_manager.stop_load_test()

if __name__ == "__main__":
    asyncio.run(main())