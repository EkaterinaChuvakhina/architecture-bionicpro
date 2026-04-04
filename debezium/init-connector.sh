#!/bin/sh
set -e

echo "=== Ждём запуска Debezium ==="
until curl -s -f -X GET http://debezium:8083/connectors > /dev/null; do
  echo "Debezium ещё не готов... ждём 2 секунды"
  sleep 2
done

echo "=== Debezium готов ==="

curl -X POST http://debezium:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "crm-customers-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "tasks.max": "1",
      "database.hostname": "crm_db",
      "database.port": "5432",
      "database.user": "crm_user",
      "database.password": "crm_password",
      "database.dbname": "crm_db",
      "database.server.name": "crm",
      "table.include.list": "public.customers",
      "plugin.name": "pgoutput",
      "slot.name": "debezium_slot_customers",
      "publication.name": "dbz_publication_customers",
      "publication.autocreate": "true",
      "topic.prefix": "crm",
      "transforms": "unwrap",
      "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
      "transforms.unwrap.drop.tombstones": "false",
      "transforms.unwrap.delete.handling.mode": "rewrite",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false"
    }
  }' || echo "Connector уже существует (нормально)"

echo "=== Connector готов ==="
