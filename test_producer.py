import signal
import sys
from confluent_kafka import Producer
import time
import random
import json

# p = Producer({'bootstrap.servers': 'my-cluster-kafka-external-bootstrap.kafka.svc.cluster.local:32100'})
p = Producer({'bootstrap.servers': 'storage-worker03-10gb:32100'})

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Gracefully handle Ctrl+C
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Flushing remaining messages...')
    p.flush()  # Flush any remaining messages before exiting
    sys.exit(0)

# Set the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

for i in range(100):  # Replace with while True for continuous loop
    data = {
        "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "WTUR-01": random.randint(1, 100),
        "WTUR-02": random.randint(1, 100),
        "WTUR-03": random.randint(1, 100)
    }
    value = json.dumps(data).encode('utf-8')

    p.poll(0)
    p.produce('test-topic', value=value, callback=delivery_report)

    time.sleep(1)

p.flush()
