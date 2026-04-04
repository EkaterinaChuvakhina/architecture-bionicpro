USE bionicpro;

DROP VIEW IF EXISTS  bionicpro.mv_kafka_to_customers_raw;

CREATE MATERIALIZED VIEW mv_kafka_to_customers_raw
TO bionicpro.customers_raw
AS
SELECT
    JSONExtractUInt(message, 'id') AS id,
    JSONExtractString(message, 'name') AS name,
    JSONExtractString(message, 'email') AS email,
    toUInt8OrNull(base64Decode(JSONExtractString(message, 'age', 'value'))) AS age,
    JSONExtractString(message, 'gender') AS gender,
    JSONExtractString(message, 'country') AS country,
    JSONExtractString(message, 'address') AS address,
    JSONExtractString(message, 'phone') AS phone,
    JSONExtractBool(message, '__deleted') AS __deleted
FROM kafka_customers
WHERE isValidJSON(message)
  AND JSONHas(message, 'id');