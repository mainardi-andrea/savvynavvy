import boto3
import pandas as pd
from gpxcsv import gpxtolist
from pathlib import Path
from config import config
from sql_queries import sql_queries


def glob_files(folder: str) -> list:
    '''
    Returns a list of all the gpx files in the input folder
    '''
    
    gpx_folder = Path(folder)

    return [x for x in gpx_folder.glob('*.gpx')]


def gpxs_to_df(filelist: list) -> pd.DataFrame:
    '''
    iterates through the filelist and appends all the data to a dataframe
    '''
    
    df = pd.DataFrame()
    
    for filepath in filelist:
        temp_df = pd.DataFrame(gpxtolist(str(filepath)))
        df = pd.concat([df, temp_df], ignore_index=True)
        
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Removes outliers with negative speed and course
    '''

    return df[~((df["speed"]<0) | (df["course"]<0))]


def timestamp_conversion(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Casts timestamp column to python datetime type
    '''

    df.time = pd.to_datetime(df.time)

    return df


def dataframe_to_s3(df: pd.DataFrame) -> None:
    '''
    Writes dataframe as csv file 
    uploads it to s3
    deletes the local csv
    '''

    local_filepath = config["local_csv_filepath"]
    df.to_csv(local_filepath)

    s3 = boto3.client('s3', aws_access_key_id=config["aws_id"], aws_secret_access_key=config["aws_secret"])
    s3.put_object(
        Body=local_filepath,
        Bucket=config["s3_bucket"],
        Key=config["s3_csv_filepath"],
    )

    Path(local_filepath).unlink()

    return


def load_to_redshift(queries: list) -> None:
    '''
    deletes redshift table if existing
    creates new table
    copies csv to table
    '''

    redshift = boto3.client('redshift', aws_access_key_id=config["aws_id"], aws_secret_access_key=config["aws_secret"])

    for query in queries:
        redshift.execute_statement(
            ClusterIdentifier=config["redshift_cluster"], 
            Database=config["database"], 
            SecretArn=config["secret_arn"],
            Sql=query)
    
    return


def main():
    
    filelist = glob_files(config["gpx_folder"])

    df = gpxs_to_df(filelist)

    df = remove_outliers(df)

    df = timestamp_conversion(df)

    dataframe_to_s3(df)

    load_to_redshift(sql_queries)


if __name__ == "__main__":
    main()
