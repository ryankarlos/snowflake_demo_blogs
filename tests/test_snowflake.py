import os

import pytest

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

