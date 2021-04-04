import configparser
import psycopg2
from lib import aws_config, aws
from lib import redshift_connection
from sql_queries import copy_table_queries, insert_table_queries

def load_staging_tables(cur, conn, config):
    """
    This method is used to load ingest the raw data located in S3 into into Redshift. 
    The data ingestion is the following:
    
        s3://udacity-dend/log_data      -> sparkify:staging_events
        s3://udacity-dend/staging_songs -> sparkify:staging_songs
    
    Args:
        cur (psycopg2.extensions.cursor): psycopg2 cursor object used to run queries against a database
        conn (psycopg2.extensions.connection): psycopg2 connection object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
    """
    
    song_data_uri = config.song_data
    events_data_uri = config.log_data
    events_data_json = config.log_jsonpath
    
    print_songs = "\nCopying song data\nS3 URI: {}".format(song_data_uri)
    print_events = "\nCopying event logs\nS3 URI: {}".format(events_data_uri)
    
    for query, out in zip(copy_table_queries, [print_songs, print_events]):
        print(out)
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn, config):
    """
    This method is used to re-allocate the log and song data present in the staging tables 
    across the database tables: songplays, users, songs, artists and time. 
    This way, the information in the database is modeled in a star-shaped schema  
    
    Args:
        cur (psycopg2.extensions.cursor): psycopg2 cursor object used to run queries against a database
        conn (psycopg2.extensions.connection): psycopg2 connection object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
    """
    
    print("\nIngesting data into songplays, users, songs, artists and time tables\n")
    
    for query in insert_table_queries:
        print(query+"\n")
        cur.execute(query)
        conn.commit()


def main():
    
    config_path = "../dwh.cfg"
    config = aws_config(config_path)
    aws_clients = aws(config)
    
    redshift = aws_clients.redshift
    
    conn, cur = redshift_connection(redshift, config)
    
    bucket = aws_clients.s3.Bucket("udacity-dend")
    
    # Uncomment these lines to visualize the S3 paths of the song_data
    # The same can be done for the event logs
    """
    for obj in bucket.objects.filter(Prefix="song_data/A/"):
        print(obj)
    """
    
    rolearn_dwhS3 = aws_clients.iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']
    
    #load_staging_tables(cur, conn, config)
    
    insert_tables(cur, conn, config)

    conn.close()


if __name__ == "__main__":
    main()