from confluent_kafka import Consumer, KafkaException, KafkaError
import mysql.connector
import json
from datetime import datetime

# MySQL 연결 설정
mysql_conf = {
    'user': 'root',
    'password': '1234',
    'host': '192.168.1.33',
    'port': 31990,
    'database': 'test'
}

# MySQL 테이블 생성 (필요할 경우)
table_creation_query = """
CREATE TABLE IF NOT EXISTS kafka_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    time TIMESTAMP,
    wt_01 INT,
    wt_02 INT,
    wt_03 INT
);
"""

# MySQL 데이터베이스 연결 및 테이블 생성
mysql_conn = mysql.connector.connect(**mysql_conf)
mysql_cursor = mysql_conn.cursor()
mysql_cursor.execute(table_creation_query)
mysql_conn.commit()

# Kafka 소비자 설정
kafka_conf = {
    'bootstrap.servers': 'storage-worker03-10gb:32100',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(kafka_conf)

# 구독할 토픽 설정
topic_name = 'test-topic'
consumer.subscribe([topic_name])

try:
    print(f"Subscribed to topic: {topic_name}")
    while True:
        # 메시지 수신
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            else:
                raise KafkaException(msg.error())
        else:
            # 메시지를 성공적으로 수신한 경우
            data = json.loads(msg.value().decode('utf-8'))
            print(f"Received message: {data}")

            # MySQL에 저장할 데이터 추출 및 형식 변환
            time_str = data.get('time')
            time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
            wt_01 = data.get('WTUR-01')
            wt_02 = data.get('WTUR-02')
            wt_03 = data.get('WTUR-03')

            # 데이터베이스에 삽입
            insert_query = """
            INSERT INTO kafka_messages (time, wt_01, wt_02, wt_03)
            VALUES (%s, %s, %s, %s);
            """
            mysql_cursor.execute(insert_query, (time, wt_01, wt_02, wt_03))
            mysql_conn.commit()
            print("Data inserted into MySQL")

except KeyboardInterrupt:
    print("Consumer stopped by user")

finally:
    # 리소스 해제
    consumer.close()
    mysql_cursor.close()
    mysql_conn.close()
