import os

import pytest
from unittest import mock
from unittest.mock import MagicMock
import pytest
from moto import mock_aws
import moto
from datetime import datetime
from snowflake_op import (
    SnowflakeOperator
)

@pytest.fixture(scope="function")
def dummy_dataframe():
    return pd.DataFrame(
        data=np.random.randint(1, 10, (5, 3)), columns=["col1", "col2", "col3"]
    )

@pytest.fixture(scope="function")
def snowflake_conn():
    conn = SnowflakeOperator()
    return conn


def test_execute(snowflake_conn, mocker):
    mocked_execute = mocker.patch(
        "snowflake_op.SnowflakeOperator.execute"
    )
    snowflake_conn.execute(sql="SELECT * FROM db.schema.table limit 10;")
    assert mocked_execute.call_count == 1
    assert mocked_execute.call_args.kwargs == {
        "sql": "SELECT * FROM db.schema.table limit 10;"
    }


def test_to_external_stage(self):
    with mock.patch(
        "snowflake_op.SnowflakeOperator"
    ) as mock_conn:

        snowflake.to_external_stage(
            prefix="dummy_prefix", table_name="demo_table", external_stage="@DUMMYDB.DUMMYSCHEMA.STAGE"
        )
        current_date = datetime.today().strftime("%Y-%m-%d")
        mock_conn.return_value.execute.assert_called_once_with(
            sql=f"REMOVE @DUMMYDB.DUMMYSCHEMA.STAGE/{current_date}/dummy_prefix; COPY INTO @DUMMYDB.DUMMYSCHEMA.STAGE"/{current_date}/dummy_prefix/data.csv.gz FROM demo_table FILE_FORMAT = (RECORD_DELIMITER = '\n' EMPTY_FIELD_AS_NULL = false NULL_IF =('null') ) single=true max_file_size=4900000000 HEADER=TRUE;"
        )

        mock_conn.reset_mock()
        # test case where single is set to False with different external stage. Should invoke other copy into query
        snowflake.to_external_stage(
            prefix="dummy_prefix",
            table_name="demo_table",
            single=False,
            external_stage="@NEWSTAGE",
            max_file_size=16000000,
        )
        mock_conn.return_value.execute.assert_called_once_with(
            sql=f"REMOVE @NEWSTAGE/{current_date}/dummy_prefix; COPY INTO @NEWSTAGE/{current_date}/dummy_prefix/ FROM demo_table FILE_FORMAT = (RECORD_DELIMITER = '\n' EMPTY_FIELD_AS_NULL = false NULL_IF =('null') ) max_file_size=16000000 HEADER=TRUE;"
        )

# TODO use moto library for mocking aws services in future.
@mock.patch("shared_utils.template.data_mover.snowflake_mover.SnowflakeConnector")
@mock.patch("shared_utils.template.data_mover.bucket_mover.boto3.resource")
def test_export_local_to_s3(self, mocked_aws_resource, _):
    snowflake = SnowflakeMover("file.cred")
    # mock_bucket.return_value.objects.filter.return_value = ["dir/subfolder/data.csv.gz"]
    snowflake.export_to_local_from_stage(
        prefix="dummy_prefix", table_name="demo_table", external_stage="@NEWSTAGE", bucket="dummy_bucket"
    )
    current_date = datetime.today().strftime("%Y-%m-%d")
    snowflake.connector.execute.assert_called_once_with(
        sql=f"REMOVE @NEWSTAGE/{current_date}/dummy_prefix;"
        f" COPY INTO @NEWSTAGE/{current_date}/dummy_prefix/data.csv.gz FROM demo_table FILE_FORMAT = (RECORD_DELIMITER = '\n' EMPTY_FIELD_AS_NULL = false NULL_IF =('null') ) "
        f"single=true max_file_size=4900000000 HEADER=TRUE;"
    )

    mock_bucket = mocked_aws_resource.return_value.Bucket

    mock_bucket.assert_called_once_with(
        "dummy_bucket",
    )
    mock_bucket.return_value.objects.filter.assert_called_once_with(
        Prefix=f"{current_date}/dummy_prefix"
    )
    # mock_bucket.return_value.download_file.assert_called_once_with("dir/subfolder/data.csv.gz", "results/data.csv.gz")

@mock.patch("shared_utils.template.data_mover.bucket_mover.boto3.resource")
@patch("snowflake_op.SnowflakeOperator")
def test_import_to_snowflake_from_s3(self, mock_conn, mock_aws_resource):
    from datetime import datetime

    file = "snowflake_table_data.csv"
    current_date = datetime.today().strftime("%Y-%m-%d")
    mock_bucket = mock_aws_resource.return_value.Bucket
    self.m.import_to_snowflake(file, "dummy_prefix", "demo-table", "dummy_stage")
    mock_bucket.return_value.upload_file.assert_called_once_with(
        "snowflake_table_data.csv",
        f"{current_date}/dummy_prefix/snowflake_table_data.csv",
    )
    mock_conn.return_value.execute.assert_called_once_with(
        sql=f"COPY INTO demo-table FROM @dummy_stage/{current_date}/dummy_dag/dummy_task/snowflake_table_data.csv FILE_FORMAT = (NULL_IF =('null') SKIP_HEADER = 1);"
    )

