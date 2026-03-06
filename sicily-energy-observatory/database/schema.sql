CREATE TABLE IF NOT EXISTS raw_generation_15min (
    timestamp TIMESTAMP PRIMARY KEY,
    region VARCHAR,
    generation_total_MW DOUBLE,
    generation_solar_MW DOUBLE,
    generation_wind_MW DOUBLE,
    generation_hydro_MW DOUBLE,
    generation_gas_MW DOUBLE,
    generation_fossil_MW DOUBLE,
    source VARCHAR,
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generation_hourly (
    timestamp TIMESTAMP PRIMARY KEY,
    region VARCHAR,
    generation_total_MW DOUBLE,
    generation_solar_MW DOUBLE,
    generation_wind_MW DOUBLE,
    generation_hydro_MW DOUBLE,
    generation_gas_MW DOUBLE,
    generation_fossil_MW DOUBLE,
    renewables_share DOUBLE,
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generation_daily (
    date DATE PRIMARY KEY,
    region VARCHAR,
    generation_total_MW DOUBLE,
    generation_solar_MW DOUBLE,
    generation_wind_MW DOUBLE,
    generation_hydro_MW DOUBLE,
    generation_gas_MW DOUBLE,
    generation_fossil_MW DOUBLE,
    renewables_share DOUBLE,
    peak_timestamp TIMESTAMP,
    peak_generation_MW DOUBLE,
    renewable_dominance_pct DOUBLE,
    load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
