from snowflake.snowpark.functions import udf
import snowflake.snowpark.types as T
import numpy

def register_udf(session):
    # User defined function
    add_random = udf(lambda x: x + numpy.random.normal() if x is not None else 0, 
                     return_type= T.FloatType(), 
                     input_types = [T.FloatType()]
                     )
    return add_random

def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized = "table", packages = ["pandas", "numpy"],  python_version="3.11")

    # User defined function
    @udf
    def add_one(x: int) -> int:
        x = 0 if not x else x
        return x + 1

    # DataFrame representing an upstream model
    df = dbt.ref("my_first_dbt_model")

    # Add a new column containing the id incremented by one
    df = df.withColumn("id_plus_one", add_one(df["id"]))
    df = df.withColumn("id_plus_random", register_udf(session)(df["id"]))

    return df