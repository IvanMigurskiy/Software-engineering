import os
import signal
import sys
import json
from confluent_kafka import Consumer, KafkaError
import logging
import time
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["budget_db"]
incomes_collection = db["incomes"]
costs_collection = db["costs"]

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# Signal handler for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    running = False
    logger.info("Shutting down receiver...")

signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # Handle Docker stop signals

def main():
    """Receives messages from Kafka in a loop."""
    time.sleep(10)
    consumer = None  # Initialize consumer outside the try block
    try:
        # Kafka Consumer Configuration
        consumer_config = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'my_consumer_group',
            'auto.offset.reset': 'earliest'  # Start from beginning if no offset exists
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe(['incomes', 'costs'])
        logger.info(f"Subscribed to topic: {'incomes costs'}")

        while running:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
            try:
                data = json.loads(msg.value().decode('utf-8'))
                topic = msg.topic()
                if topic == 'incomes':
                    db.incomes.insert_one(data)
                    logger.info(f"Inserted income: {data['_id']}")
                elif topic == 'costs':
                    db.costs.insert_one(data)
                    logger.info(f"Inserted cost: {data['_id']}")
                else:
                    logger.info(f"Unknown topic: {data['_id']}")

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        if consumer: # Check if consumer was initialized
            logger.info("Closing consumer...")
            consumer.close()
            logger.info("Consumer closed.")
        logger.info("Receiver exiting.")
        client.close()  
        
if __name__ == "__main__":
    main()