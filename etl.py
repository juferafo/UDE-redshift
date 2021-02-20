import configparser
import psycopg2
from lib import aws_config, aws
from lib import redshift_connection
from sql_queries import copy_table_queries, insert_table_queries

def load_staging_tables(cur, conn, config):
    """
    This method is used to load the ...
    
    Args:
        cur ():
        conn ():
        config ():
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
    This method is used to...
    
    Args:
        cur ()
        conn ()
        config ()
    """
        
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    config_path = "../dwh.cfg"
    config = aws_config(config_path)
    aws_clients = aws(config)
    
    redshift = aws_clients.redshift
    
    
    conn, cur = redshift_connection(redshift, config)
    
    bucket = aws_clients.s3.Bucket("udacity-dend")
    
    # Uncommnet these lines to visualize the S3 paths of the song_data
    # The same can be done for the event logs
    """
    for obj in bucket.objects.filter(Prefix="song_data/A/"):
        print(obj)
    """
    
    rolearn_dwhS3 = aws_clients.iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']
    
    load_staging_tables(cur, conn, config)
    
    
    
    
    
    #insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()