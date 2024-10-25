# snowflake_demo_blogs


### External Snowflake Stage to Copy to S3 bucket

With Snowflake, you can use an external stage to connect to S3 bucket in AWS. The external stage stores an S3-compliant API endpoint, bucket name and path, and credentials. To allow users to load and unload data from and to your storage locations, one can grant privileges to stage roles. For more details on how to set this up, please refer to the snowflake documentation https://docs.snowflake.com/en/user-guide/data-load-s3-compatible-storage#creating-an-external-stage-for-s3-compatible-storage


Once the stage is setup, users can load and unload data https://docs.snowflake.com/en/user-guide/data-load-s3-compatible-storage#loading-and-unloading-data.  For bulk loading  use the COPY INTO <table> command or bulk data unloading using the COPY INTO <location> command. 

In this scenario, we want to unload data from the table into S3. 

In the example below, we are unloading data from the training table TRAIN_SAMPLE_10000 table in snowflake into train/training_sample_10000  subpath in bucket and path defined in stage named DEMO_DB.DEMO_SCHEMA.STAGE_DEMO. We specify format as parquet and the first row as headers.

COPY INTO '@DEMO_DB.DEMO_SCHEMA.STAGE_DEMO/train/training_sample_10000'
FROM DEMO_DB.DEMO_SCHEMA.STAGE_DEMO.TRAIN_SAMPLE_10000
FILE_FORMAT = (type = 'parquet')
HEADER = TRUE
OVERWRITE=TRUE;


In the Snowflake staging bucket , we can see the data in the train prefix with the object name beginning training_sample_10000 and stored as parquet file.
