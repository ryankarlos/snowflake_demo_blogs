import posixpath
from datetime import datetime
from pathlib import Path
from typing import Optional

import boto3
from snowflake.connector.constants import CONNECTIONS_FILE
import shutil
import os
import snowflake.connector


class SnowflakeOperator:

    def __init__(self, connections_name: Optional[str]='default_connection'):

        self.conn = snowflake.connector.connect(connections_name)
        
    def execute(self, query, asynchronous=False):
        with self.conn.cursor() as cur:
            if not asynchronous:
                cur = self.conn.cursor()
                cur.execute(query)
            else:
                cur.execute_async('select count(*) from table(generator(timeLimit => 25))')
            results = cur.fetchall()
        return results

    def check_query_status(self, cur):
        import time
        # Wait for the query to finish running.
        query_id = cur.sfqid
        while self.conn.is_still_running(self.conn.get_query_status(query_id)):
            time.sleep(1)

    def close_connection(self):
        self.conn.close()

    def _download_from_s3(self, prefix, local_dir, bucket):
        """
        The uses the method provided by the AWS SDK for Python to download files
        which accepts the names of the bucket and object to download and the filename to save the file to.
        Args:
            prefix: object prefix to download objects
            local_dir: The name of the output file to save it to locally
            bucket: Name of the bucket

        Returns:
            None
        """
        
        s3_resource = boto3.resource("s3")
        bucket = s3_resource.Bucket(bucket)
        objs = bucket.objects.filter(Prefix=prefix)
        shutil.rmtree(local_dir, ignore_errors=True)
        Path(local_dir).mkdir(exist_ok=True)
        for obj in objs:
            local_filename = obj.key.split("/")[-1]
            bucket.download_file(obj.key, f"{local_dir}/{local_filename}")

    def _import_from_s3_to_snowflake(
        self,
        obj_key: str,
        table_name: str,
        external_stage: str,
    ) -> None:
        """
        This method imports data from S3 bucket to snowflake table using the Snowflake
        COPY INTO command https://docs.snowflake.com/en/sql-reference/sql/copy-into-table
        for data loading from existing external stage created in warehouse
        (which maps to the snowflake bucket)
        Args:
            obj_key: s3 bucket object key
            table_name: The name of the table
            cred_file: the path to cred_file. Defaults to constant CONNECTIONS_FILE
            external_stage: The external stage created in snowflake warhouse. Defaults to "EDLDATASCIENCEDB.EDLDSUSER.STG_DS_AWS_POC"

        Returns:
            None

        """
        self.execute(query=f"COPY INTO {table_name} FROM {external_stage}/{obj_key} FILE_FORMAT = (NULL_IF =('null') SKIP_HEADER = 1);")


    def _upload_to_s3_from_local(self,  file: str, key: str, bucket: str) -> None:
        """Loads data from local filesystem to S3

        Args:
            file: The filepath in local machine
            key: The s3 object key associated with the file to load
            bucket: The name of the S3 bucket to load data into.

        Returns:
            None
        """
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket)
        bucket.objects.filter(Prefix=key).delete()
        bucket.upload_file(file, key)



    def import_to_table_from_local(self, local_file: str, prefix: str, bucket: str, table_name: str, external_stage: str) -> None:
        """Import a file from local filesystem on your machine to a snowflake table

        Args:
            local_file:  The filepath on local machine.
            prefix: prefix of s3 bucket
            bucket: s3 bucket to upload data to mapped to snowflake stage
            table_name: snowflake_table_name to load data into.
            external_stage

        Returns:
            None
        """
        current_date = datetime.today().strftime("%Y-%m-%d")
        obj_key = f"{current_date}/{prefix}/{local_file}"
        self._upload_to_s3_from_local(local_file, obj_key, bucket)
        self._import_from_s3_to_snowflake(obj_key, table_name, external_stage)


    def export_to_local_from_stage(
        self,
        prefix: str,
        table_name: str,
        bucket: str,
        external_stage: str,
        local_dir: Optional[str] = "results",
        single: Optional[bool] = True,
        max_file_size: Optional[int] = 4900000000,
    ):
        """Exports table from snowflake to local via S3

        This uses the snowflake export to stage method to copy data from table to snowflake external stage mapped to S3 bucket and then
        download data from the S3 bucket to local.

        Args:
            table_name: Name of the table in Snowflake to export data from
            local_dir: local dir to store the results. Defaults to 'results'
            single: Whether to export to single file or multiple files (parallel operations). Defaults to True
            max_file_size: The max file size (max allowed is 5GB). Defaults to 4.9 GB.
            bucket: S3 bucket mapped to snowflake external stage. Defaults to constant SNOWFLAKE_S3_BUCKET
            external_stage: The snowflake external stage preconfigured to map to S3 bucket for loading/unloading
        Returns:
            None

        """
        self.to_external_stage(
            prefix, table_name, single, max_file_size, external_stage
        )
        current_date = datetime.today().strftime("%Y-%m-%d")
        prefix = f"{current_date}/{prefix}"
        self._download_from_s3(prefix, local_dir, bucket)

    def _to_external_stage(
        self,
        prefix: str,
        table_name: str,
        external_stage: str,
        single: Optional[bool] = True,
        max_file_size: Optional[int] = 4900000000,
    ):
        """
        This unloads the data to a single file by default. https://docs.snowflake.com/en/user-guide/data-unload-considerations#unloading-to-a-single-file
        if performance needs to be increased, then consider setting single arg to false to generate partition files to take advantage
        of parallel operations in snowflake. Data format defaults to CSV and compression gz
        Args:
            dag_name: The name of the airflow dag running this export task
            task_name:  The name of the task running the export job in the dag
            table_name: Name of the table in Snowflake to export data from
            single: Whether to export to single file or multiple files (parallel operations). Defaults to True
            max_file_size: The max file size (max allowed is 5GB). Defaults to 4.9 GB.
            external_stage: The snowflake external stage preconfigured to map to S3 bucket for loading/unloading

        """
        current_date = datetime.today().strftime("%Y-%m-%d")
        key = f"{current_date}/{prefix}"
        if single:
            self.connector.execute(
                sql=f"REMOVE {external_stage}/{key}; COPY INTO {external_stage}/{key}/data.csv.gz FROM "
                f"{table_name} FILE_FORMAT = (RECORD_DELIMITER = '\n' EMPTY_FIELD_AS_NULL = false NULL_IF =('null') ) "
                f"single=true max_file_size={max_file_size} HEADER=TRUE;"
            )
        else:
            self.connector.execute(
                sql=f"REMOVE {external_stage}/{key}; COPY INTO {external_stage}/{key}/ FROM "
                f"{table_name} FILE_FORMAT = (RECORD_DELIMITER = '\n' EMPTY_FIELD_AS_NULL = false NULL_IF =('null') ) max_file_size={max_file_size} HEADER=TRUE;"
            )
