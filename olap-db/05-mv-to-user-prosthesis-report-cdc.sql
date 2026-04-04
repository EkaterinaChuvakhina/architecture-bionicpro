USE bionicpro;

DROP VIEW IF EXISTS  bionicpro.mv_to_user_prosthesis_report_cdc;

DETACH TABLE IF EXISTS bionicpro.user_prosthesis_report_cdc;
DROP TABLE IF EXISTS  bionicpro.user_prosthesis_report_cdc;

CREATE TABLE  bionicpro.user_prosthesis_report_cdc (
                                            user_id              UInt32,
                                            name                 String,
                                            email                String,
                                            age                  Nullable(UInt8),
                                            gender               String,
                                            country              String,
                                            total_signals        UInt64,
                                            first_signal         Nullable(DateTime),
                                            last_signal          Nullable(DateTime),
                                            days_with_data       UInt32,
                                            avg_amplitude        Float64,
                                            avg_frequency        Float64,
                                            avg_duration         Float64,
                                            most_used_prosthesis String,
                                            most_used_muscle     String,
                                            updated_at           DateTime DEFAULT now()
)
    ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id
PARTITION BY toYYYYMM(updated_at);