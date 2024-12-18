-- This is your Cortex Project.
-----------------------------------------------------------
-- SETUP
-----------------------------------------------------------
use role ACCOUNTADMIN;
use warehouse SO_WAREHOUSE;
use database FINANCE__ECONOMICS;
use schema CYBERSYN;

-- Inspect the first 10 rows of your training data. This is the data we'll use to create your model.


DROP VIEW IF EXISTS DEMO_SNOWFLAKE.DEMO_SCHEMA.FHFA_UNIFORM_APPRAISAL_TIMESERIES_v1;
-- -- Prepare your training data. Timestamp_ntz is a required format. Also, only include select columns.
CREATE OR REPLACE VIEW DEMO_SNOWFLAKE.DEMO_SCHEMA.FHFA_UNIFORM_APPRAISAL_TIMESERIES_v1 AS SELECT
    to_timestamp_ntz(DATE) as DATE_v1,
    VAL AS VALUE,
FROM 
(select DATE, AVG(VALUE) AS VAL  FROM FINANCE__ECONOMICS.CYBERSYN.FHFA_HOUSE_PRICE_TIMESERIES
GROUP BY DATE);



-- -----------------------------------------------------------
-- -- CREATE PREDICTIONS
-- -----------------------------------------------------------
-- -- Create your model.
CREATE OR REPLACE SNOWFLAKE.ML.FORECAST DEMO_SNOWFLAKE.DEMO_SCHEMA.time_series_forecasting(
    INPUT_DATA => SYSTEM$REFERENCE('VIEW', 'DEMO_SNOWFLAKE.DEMO_SCHEMA.FHFA_UNIFORM_APPRAISAL_TIMESERIES_v1'),
    TIMESTAMP_COLNAME => 'DATE_v1',
    TARGET_COLNAME => 'VALUE',
    CONFIG_OBJECT => { 'ON_ERROR': 'SKIP' }
);

-- Generate predictions and store the results to a table.
BEGIN
    -- This is the step that creates your predictions.
    CALL DEMO_SNOWFLAKE.DEMO_SCHEMA.time_series_forecasting!FORECAST(
        FORECASTING_PERIODS => 150,
        -- Here we set your prediction interval.
        CONFIG_OBJECT => {'prediction_interval': 0.9}
    );
    -- These steps store your predictions to a table.
    LET x := SQLID;
    CREATE OR REPLACE TABLE  DEMO_SNOWFLAKE.DEMO_SCHEMA.My_forecasts_2024_12_18 AS SELECT * FROM TABLE(RESULT_SCAN(:x));
END;

-- View your predictions.
SELECT * FROM  DEMO_SNOWFLAKE.DEMO_SCHEMA.My_forecasts_2024_12_18

-----------------------------------------------------------
-- INSPECT RESULTS
-----------------------------------------------------------

-- -- Inspect the accuracy metrics of your model. 
-- CALL DEMO_SNOWFLAKE.DEMO_SCHEMA.time_series_forecasting!SHOW_EVALUATION_METRICS();


