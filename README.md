# snowflake_demo_blogs


## External Snowflake Stage to Copy to S3 bucket

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

### Executing Terraform modules


The terraform folder contains the scripts necessary for creating the resources required for integrating external stage in snowflake to import/export data  into S3 bucket: 

* S3 bucket with option of AES256, KMS encryption using AWS managed key  
* Bucket policy to enforce ssl
* IAM role for premissions to access the bucket (to be assumed by snowflake principal)

In addition, it also creates resources  for remote terraform state management.

* S3 bucket 
* Dynamodb table for state locking


#### Configuring SSO access to AWS account 

First confgure an iam identity center profile for your cli as per https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure

![sso_configure](screenshots/sso_configure.png)

This will cache the session credentials and the generate temp aws credentials for the role associated with your profile. These are stored in ~/.aws/ on your machine.

![sso_configure](screenshots/credentials_location.png)

**Note** you can use `export AWS_PROFILE=<your-profile>` to avoid having to pass this as an argument --profile when using any aws cli commands.

![export_profile](screenshots/export_profile.png)


Then for subsequent authentication, you can directly sign into your IAM identity center session and retrieve the aws credentials for your role. https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-login


![sso_login](screenshots/sso_login.png)


#### Deploying and Managing Resources

The main terraform script, uses variables which can be dynamically set when deploying the resources. 

The `terraform.tfvars` file in the root of the repository needs to be populated with the required variables and associated values. 

![alt text](screenshots/tfvars.png)


Now comment out the backend block in the state.tf file and run the following to create the resources. This will create the s3 bucket and dynamodn table for state management in S3

```bash
terraform init
terraform plan
terraform apply --auto-approve
```

**note** if you want to pass in variables via the [command line](https://developer.hashicorp.com/terraform/language/values/variables#variables-on-the-command-line) or set this via [environmnet variable](https://developer.hashicorp.com/terraform/language/values/variables#environment-variables) rather than using a `.tfvars`s file, please refer to  and  for the relevant commands 


Then uncomment the backend block and  re-run the commands above to reinitialise the backend tp reference the s3 bucket and dynamodb table created in the previous step for enabling remote state management.

![alt text](screenshots/tf-apply1.png)

![alt text](screenshots/tf-apply2.png)

