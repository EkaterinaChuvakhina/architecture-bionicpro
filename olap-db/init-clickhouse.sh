#!/bin/bash
set -e

echo "=== Инициализация ClickHouse (bionicpro) ==="

echo "Выполняем миграции в правильном порядке..."

for script in /scripts/0[1-6]-*.sql; do
  if [ -f "$script" ]; then
    filename=$(basename "$script")
    echo "Выполняем: $filename"

    if ! clickhouse-client \
           --host olap_db \
           --user default \
           --password "" \
           --multiquery \
           --query "$(cat "$script")"; then
      echo "КРИТИЧЕСКАЯ ОШИБКА в $filename"
      echo "Инициализация остановлена!"
      exit 1
    fi
    echo "$filename выполнен успешно"
  fi
done

echo "Инициализация ClickHouse успешно завершена!"

docker compose exec olap_db clickhouse-client -q "
SELECT
    'customers_raw'            AS table, count(*) AS rows FROM bionicpro.customers_raw
UNION ALL
SELECT
    'user_prosthesis_report_cdc' AS table, count(*) AS rows FROM bionicpro.user_prosthesis_report_cdc;
"