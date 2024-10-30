from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka 소비자 설정
conf = {
    'bootstrap.servers': 'storage-worker03-10gb:32100',  # Kafka 브로커 주소
    'group.id': 'my-consumer-group',  # Consumer 그룹 ID
    'auto.offset.reset': 'earliest'  # 토픽 처음부터 읽기
}

# Consumer 객체 생성
consumer = Consumer(conf)

# 구독할 토픽 설정
topic_name = 'test-topic'
consumer.subscribe([topic_name])

try:
    print(f"Subscribed to topic: {topic_name}")
    while True:
        # 메시지 수신
        msg = consumer.poll(timeout=1.0)  # 타임아웃 설정 (1초)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # 파티션의 끝에 도달했을 때
                print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            else:
                raise KafkaException(msg.error())
        else:
            # 메시지를 성공적으로 수신한 경우
            print(f"Received message: {msg.value().decode('utf-8')} from {msg.topic()} [{msg.partition()}]")

except KeyboardInterrupt:
    # Ctrl+C로 프로그램 종료
    print("Consumer stopped by user")

finally:
    # Consumer 닫기 (리소스 해제)
    consumer.close()
