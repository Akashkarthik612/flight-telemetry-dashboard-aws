import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
import random

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/telemetry_db")

async def setup_database():
    """Initialize database with tables and sample data"""
    print("Setting up database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create main telemetry table
        await conn.execute("""
            DROP TABLE IF EXISTS telemetry CASCADE;
            
            CREATE TABLE telemetry (
                id SERIAL PRIMARY KEY,
                flight_id VARCHAR(50) NOT NULL,
                altitude DECIMAL(10,2) NOT NULL,
                speed DECIMAL(10,2) NOT NULL,
                temperature DECIMAL(10,2) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes for performance
        await conn.execute("""
            CREATE INDEX idx_flight_id ON telemetry(flight_id);
            CREATE INDEX idx_timestamp ON telemetry(timestamp);
            CREATE INDEX idx_flight_timestamp ON telemetry(flight_id, timestamp DESC);
        """)
        
        # Create alerts table for future use
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                flight_id VARCHAR(50) NOT NULL,
                alert_type VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                severity VARCHAR(20) DEFAULT 'INFO',
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX idx_alerts_flight ON alerts(flight_id);
            CREATE INDEX idx_alerts_severity ON alerts(severity);
        """)
        
        print("Database tables created successfully!")
        
        # Insert some sample data for testing
        print("Inserting sample data...")
        flights = ["FL001", "FL002", "FL003"]
        
        for flight_id in flights:
            for i in range(10):
                timestamp = datetime.utcnow() - timedelta(minutes=i*2)
                altitude = random.uniform(8000, 12000)
                speed = random.uniform(800, 950)
                temperature = 15 - (altitude / 1000) * 6.5 + random.uniform(-5, 5)
                
                await conn.execute(
                    """INSERT INTO telemetry (flight_id, altitude, speed, temperature, timestamp)
                       VALUES ($1, $2, $3, $4, $5)""",
                    flight_id, altitude, speed, temperature, timestamp
                )
        
        print(f"Sample data inserted for {len(flights)} flights!")
        
        # Verify data
        count = await conn.fetchval("SELECT COUNT(*) FROM telemetry")
        print(f"Total records in database: {count}")
        
        await conn.close()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database())