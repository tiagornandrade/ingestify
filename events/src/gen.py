import json
import datetime
from faker import Faker
from confluent_kafka import Producer
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_TOPIC = 'user-events'
ORDER_TOPIC = 'order-events'
producer = Producer({'bootstrap.servers': 'localhost:9092'})

fake = Faker()


def gen_user_event():
    """Generates a fake event for the 'user-events' topic."""
    return {
        "uuid": str(fake.uuid4()),
        "name": fake.name(),
        "city": fake.city(),
        "timestamp": datetime.datetime.now().timestamp()
    }


def gen_order_event():
    """Generates a fake event for the 'order-events' topic."""
    return {
        "order_id": str(fake.uuid4()),
        "user_id": str(fake.uuid4()),
        "product_name": fake.word(),
        "quantity": fake.random_int(min=1, max=5),
        "price": round(fake.random_number(digits=2), 2),
        "timestamp": datetime.datetime.now().timestamp()
    }


def gen_events(n, event_type='user'):
    """Generates a list of events based on the specified type."""
    if event_type == 'user':
        return [gen_user_event() for _ in range(n)]
    elif event_type == 'order':
        return [gen_order_event() for _ in range(n)]


def produce_events(events, topic):
    """Produces the events to the specified Kafka topic."""
    logger.info(f"Producing {len(events)} events to topic '{topic}'...")
    for event in events:
        event_json = json.dumps(event)
        producer.produce(topic, key=b'user_key', value=event_json.encode('utf-8'))
    producer.flush()
    logger.info(f"Events production to '{topic}' completed.")


def main():
    logging.info("Starting event generation and production script...")

    user_events = gen_events(1000, event_type='user')
    produce_events(user_events, USER_TOPIC)

    order_events = gen_events(500, event_type='order')
    produce_events(order_events, ORDER_TOPIC)

    logging.info("Script execution completed.")


if __name__ == "__main__":
    main()
