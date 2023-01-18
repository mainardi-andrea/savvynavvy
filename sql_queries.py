from config import config


gpx_table_drop = "DROP table IF EXISTS gpx;"

gpx_table_create= """
    CREATE TABLE IF NOT EXISTS gpx ( 
        track_id varchar,
        lat double precision, 
        long double precision,
        speed double precision, 
        course double precision,
        time timestamp,
        PRIMARY KEY (track_id);
"""

gpx_table_copy = f"""
    COPY gpx
    FROM 's3://{config["s3_bucket"]}/{config["s3_csv_filepath"]}'
    credentials 'aws_iam_role={config["iam_role"]}'
    CSV;
"""

sql_queries = [gpx_table_drop, gpx_table_create, gpx_table_copy]