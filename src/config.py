import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "anan_sky_db")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:7092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "fetch_external_source") # or alert_evaluator
CONSUMER_TYPE=os.getenv("CONSUMER_TYPE", "fetch_external_source") # or alert_evaluator
MODE=os.getenv("MODE", "server") # server or consumer