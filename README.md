In aerospace and aviation (think Airbus), fleets of aircraft constantly generate huge amounts of telemetry data (altitude, airspeed, temperature, pressure, etc.).
This data must be collected in real-time, stored securely, processed efficiently, and made available to engineers and dashboards for monitoring & predictive maintenance.


The challenge is:


🚦 Handling scalability (many aircraft sending data simultaneously).


🛡️ Ensuring resilience (system must not go down mid-flight).


💰 Managing costs (turn off unused environments automatically).


🔐 Enforcing security/compliance (aviation data is sensitive).


⚙️ Ensuring automation (no manual deployments, must use CI/CD + IaC).


👉 This project will simulate this environment and show how modern DevOps practices + AWS cloud services can solve these problems.

PROBLEM

So applications processing real time data streams are highly vulnerable to securty threats and also downtime, theese applications require almost 100% uptime for effective operations

Solution:
AWS - Amazon web services and leveraging aws cloud service to host this application and maintanance, which makes work easier and move away from traditional complicated on premise hosting of applications
availabilty of multi region hosting for uptime


TechStack
ECS for Hostig the application and S3 for storing logs and Lambda + Dynamo DB for storing the continous stream logs efficiently

