#!/usr/bin/env python
# coding: utf-8

"""
High-performance loader for NYC Taxi data.

Reads CSV in chunks with pandas,
loads into PostgreSQL using COPY (very fast).
"""

import click
import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine
from io import StringIO
import os

pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")
pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")
pg_db = os.getenv("PG_DB")

print("Connecting to:", pg_host, pg_port, pg_db)


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


def copy_to_postgres(df: pd.DataFrame, engine, table_name: str):
    """
    Uses PostgreSQL COPY for ultra-fast bulk insert.
    """
    # Convert DataFrame to CSV in memory
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    # Raw connection required for COPY
    conn = engine.raw_connection()
    cursor = conn.cursor()

    try:
        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", buffer)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


@click.command()
@click.option("--pg-user", default="root", help="PostgreSQL user")
@click.option("--pg-pass", default="root", help="PostgreSQL password")
@click.option("--pg-host", default="localhost", help="PostgreSQL host")
@click.option("--pg-port", default=5432, type=int, help="PostgreSQL port")
@click.option("--pg-db", default="ny_taxi", help="PostgreSQL database name")
@click.option("--target-table", default="yellow_taxi_data", help="Target table name")
@click.option("--year", default=2021, type=int)
@click.option("--month", default=1, type=int)
@click.option("--chunksize", default=100_000, type=int)
def run(
    pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, year, month, chunksize
):
    """
    Main pipeline:
    - Stream CSV
    - Create table from first chunk
    - Load chunks via COPY
    """

    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
    url = f"{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz"

    engine = create_engine(
        f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first_chunk = True

    for df_chunk in tqdm(df_iter, desc="COPYing chunks to Postgres"):
        if first_chunk:
            # Create table structure once
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
                index=False,
            )
            first_chunk = False

        # Fast bulk insert
        copy_to_postgres(df_chunk, engine, target_table)


if __name__ == "__main__":
    run()
