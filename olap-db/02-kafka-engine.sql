USE bionicpro;

DROP TABLE IF EXISTS  bionicpro.kafka_customers;

CREATE TABLE bionicpro.kafka_customers (
                                           message String
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'crm.public.customers',
    kafka_group_name = 'clickhouse-group-customers-v1',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1;