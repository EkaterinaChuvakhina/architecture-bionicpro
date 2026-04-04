USE bionicpro;

DROP VIEW IF EXISTS  bionicpro.mv_to_user_prosthesis_report_cdc;

CREATE MATERIALIZED VIEW bionicpro.mv_to_user_prosthesis_report_cdc
REFRESH EVERY 5 MINUTE
TO bionicpro.user_prosthesis_report_cdc
AS
SELECT
    c.id AS user_id,
    any(c.name)          AS name,
    any(c.email)         AS email,
    any(c.age)           AS age,
    any(c.gender)        AS gender,
    any(c.country)       AS country,

    count(e.signal_time)                                      AS total_signals,
    min(e.signal_time)                                        AS first_signal,
    max(e.signal_time)                                        AS last_signal,

    if(min(e.signal_time) IS NOT NULL,
    dateDiff('day', min(e.signal_time), max(e.signal_time)) + 1,
    0)                                                     AS days_with_data,

    round(avg(e.signal_amplitude), 2)                         AS avg_amplitude,
    round(avg(e.signal_frequency))                            AS avg_frequency,
    round(avg(e.signal_duration))                             AS avg_duration,

    argMax(e.prosthesis_type, p.cnt_p)                        AS most_used_prosthesis,
    argMax(e.muscle_group,    m.cnt_m)                        AS most_used_muscle,

    now()                                                     AS updated_at

FROM bionicpro.customers_raw AS c
    LEFT JOIN default.emg_sensor_data AS e
ON c.id = e.user_id

    LEFT JOIN (
    SELECT
    user_id,
    prosthesis_type,
    count(*) AS cnt_p
    FROM default.emg_sensor_data
    GROUP BY user_id, prosthesis_type
    ) p
    ON p.user_id = e.user_id
    AND p.prosthesis_type = e.prosthesis_type

    LEFT JOIN (
    SELECT
    user_id,
    muscle_group,
    count(*) AS cnt_m
    FROM default.emg_sensor_data
    GROUP BY user_id, muscle_group
    ) m
    ON m.user_id = e.user_id
    AND m.muscle_group = e.muscle_group

WHERE c.__deleted = false
  AND c.id IS NOT NULL

GROUP BY c.id;

SELECT 'Refreshable MV mv_to_user_prosthesis_report_cdc успешно создана' AS status;