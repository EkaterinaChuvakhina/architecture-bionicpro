USE bionicpro;

DROP TABLE IF EXISTS bionicpro.customers_raw;

CREATE TABLE bionicpro.customers_raw (
                                         id UInt32,
                                         name String,
                                         email String,
                                         age Nullable(UInt8),
                                         gender String,
                                         country String,
                                         address String,
                                         phone String,
                                         __deleted Bool DEFAULT false,
                                         _inserted_at DateTime DEFAULT now()
) ENGINE = Rep