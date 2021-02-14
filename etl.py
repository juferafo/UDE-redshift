import configparser
import psycopg2
from lib import aws_config, aws
from lib import redshift_connection
from sql_queries import copy_table_queries, insert_table_queries

def load_staging_tables(cur, conn):
    """
    This method is used to load the data...
    """
    
    # list files:
    
    
    #for query in copy_table_queries:
    #    cur.execute(query)
    #    conn.commit()


def insert_tables(cur, conn):
    """
    This method is used to...
    """
        
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    config_path = "../dwh.cfg"
    conn, cur, aws_clients, config = redshift_connection(config_path)
    
    bucket = aws_clients.s3.Bucket("udacity-dend")
    
    for obj in bucket.objects.filter(Prefix="song_data/A/"):
        print(obj)
        break
    
    rolearn_dwhS3 = aws_clients.iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']
    
    query = """
    copy staging_songs from 's3://udacity-dend/song_data' iam_role '{}' json 'auto';
    """.format(rolearn_dwhS3)
    
    print(query)
    cur.execute(query)
    #load_staging_tables(cur, conn)
    
    
    
    
    
    #insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()