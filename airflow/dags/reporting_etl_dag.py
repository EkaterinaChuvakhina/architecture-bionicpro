from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
import psycopg2.extras
import json

default_args = {
    "owner": "bionicpro",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="bionicpro_report_etl",
    default_args=default_args,
    description="BionicPRO ETL: CRM → ClickHouse",
    schedule="0 * * * *",           # каждый час
    catchup=False,
    tags=["bionicpro", "etl", "clickhouse"],
)


def load_customers_to_clickhouse(**context):
    """Загружает таблицу customers из Postgres в ClickHouse"""
    print("🚀 Starting load_customers_to_clickhouse...")

    # 1. Подключение к PostgreSQL (CRM)
    conn = psycopg2.connect(
        host="crm_db",          # ← правильное имя сервиса
        port=5432,              # ← внутренний порт!
        dbname="crm_db",
        user="crm_user",
        password="crm_password",
        connect_timeout=10
    )
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM customers;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"✅ Извлечено {len(rows)} записей из customers")

    if not rows:
        print("⚠️ Нет данных для загрузки")
        return 0

    # 2. Подключение к ClickHouse
    import clickhouse_connect

    client = clickhouse_connect.get_client(
        host="olap_db",         # ← правильное имя сервиса
        port=8123,
        username="default",
        password="",            # у тебя пустой пароль
        database="default",
        connect_timeout=10
    )

    # Создаём базу и таблицу
    client.command("CREATE DATABASE IF NOT EXISTS bionicpro")

    client.command("""
                   CREATE TABLE IF NOT EXISTS bionicpro.customers (
                                                                      id UInt32,
                                                                      name String,
                                                                      email String,
                                                                      age UInt8,
                                                                      gender String,
                                                                      country String,
                                                                      address String,
                                                                      phone String
                   ) ENGINE = ReplacingMergeTree()
                       ORDER BY id
                   """)

    # Подготовка данных
    columns = ["id", "name", "email", "age", "gender", "country", "address", "phone"]
    data = [[row.get(col) for col in columns] for row in rows]

    # Вставка
    client.insert("bionicpro.customers", data, column_names=columns)

    print(f"✅ Успешно загружено {len(rows)} клиентов в ClickHouse → bionicpro.customers")
    return len(rows)


def refresh_user_report_summary(**context):
    """Обновляет витрину отчётов — используем таблицу из базы default"""
    import clickhouse_connect

    print("🚀 Starting refresh_user_report_summary...")

    client = clickhouse_connect.get_client(
        host="olap_db",
        port=8123,
        username="default",
        password="",
        database="default"          # ← подключаемся к default
    )

    # Создаём витрину в базе bionicpro
    client.command("""
                   CREATE TABLE IF NOT EXISTS bionicpro.user_prosthesis_report (
                                                                                   user_id UInt32,
                                                                                   name String,
                                                                                   email String,
                                                                                   age UInt8,
                                                                                   gender String,
                                                                                   country String,
                                                                                   total_signals UInt64 DEFAULT 0,
                                                                                   first_signal DateTime,
                                                                                   last_signal DateTime,
                                                                                   days_with_data UInt32 DEFAULT 0,
                                                                                   avg_amplitude Decimal(6,2) DEFAULT 0,
                       avg_frequency UInt32 DEFAULT 0,
                       avg_duration UInt32 DEFAULT 0,
                       most_used_prosthesis String,
                       most_used_muscle String,
                       updated_at DateTime DEFAULT now()
                       ) ENGINE = ReplacingMergeTree()
                       ORDER BY user_id
                       PARTITION BY toYYYYMM(updated_at)
                   """)

    # Обновляем витрину, используя таблицу из default
    client.command("""
                   INSERT INTO bionicpro.user_prosthesis_report
                   SELECT
                       c.id AS user_id,
                       any(c.name) AS name,
                       any(c.email) AS email,
                       any(c.age) AS age,
                       any(c.gender) AS gender,
                       any(c.country) AS country,
                       count(e.signal_time) AS total_signals,
                       min(e.signal_time) AS first_signal,
                       max(e.signal_time) AS last_signal,
                       dateDiff('day', min(e.signal_time), max(e.signal_time)) + 1 AS days_with_data,
                       round(avg(e.signal_amplitude), 2) AS avg_amplitude,
                       round(avg(e.signal_frequency)) AS avg_frequency,
                       round(avg(e.signal_duration)) AS avg_duration,
                       argMax(e.prosthesis_type, cnt_p) AS most_used_prosthesis,
                       argMax(e.muscle_group, cnt_m) AS most_used_muscle,
                       now() AS updated_at
                   FROM bionicpro.customers c
                       LEFT JOIN default.emg_sensor_data e ON c.id = e.user_id
                       LEFT JOIN (
                       SELECT user_id, prosthesis_type, count(*) AS cnt_p
                       FROM default.emg_sensor_data
                       GROUP BY user_id, prosthesis_type
                       ) p ON p.user_id = e.user_id AND p.prosthesis_type = e.prosthesis_type
                       LEFT JOIN (
                       SELECT user_id, muscle_group, count(*) AS cnt_m
                       FROM default.emg_sensor_data
                       GROUP BY user_id, muscle_group
                       ) m ON m.user_id = e.user_id AND m.muscle_group = e.muscle_group
                   GROUP BY c.id, c.name, c.email, c.age, c.gender, c.country
                   """)

    print("✅ Витрина user_prosthesis_report успешно обновлена")

load_customers_task = PythonOperator(
    task_id="load_customers_to_clickhouse",
    python_callable=load_customers_to_clickhouse,
    dag=dag,
)

refresh_report_task = PythonOperator(
    task_id="refresh_user_report_summary",
    python_callable=refresh_user_report_summary,
    dag=dag,
)

load_customers_task >> refresh_report_task