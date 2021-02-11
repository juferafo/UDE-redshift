import configparser
import psycopg2
import boto3
from lib import aws_config, aws
from sql_queries import create_table_queries, drop_table_queries

def drop_tables(cur, conn):
    """
    This method is used to drop all the tables in the database.
    To this end, the queries included in the global parameter drop_table_queries are executed.
    """
    
    print("\nDropping tables\n")
    for query in drop_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    This method is used to create all the tables in the database.
    To this end, the queries included in the global parameter create_table_queries are executed.
    """
    
    print("\nCreating tables\n")
    for query in create_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()

def main():
    
    # Remember to edit ../dwh.cfg according to your needs!
    config_path = '../dwh.cfg'
    #config = configparser.ConfigParser()
    #config.read(config_path)
    
    #reading config file in lib.aws_config
    config = aws_config(config_path)

    # aws object with iam and redshift clients generated from the config paramenters
    aws_clients = aws(config)  
    redshift = aws_clients.redshift
    
    cluster_identifier = config.dwh_cluster_identifier
    redshift_properties = redshift.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
    
    host = redshift_properties['Endpoint']['Address']
    connection_string = "host={} dbname={} user={} password={} port={}".format(host,\
                                                                               config.db_name,\
                                                                               config.db_user,\
                                                                               config.db_password,\
                                                                               config.db_port)
    # Careful! This will print a password on the screen!
    #print(connection_string)
    
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    print("Connection established to the cluster: redshift://{}:{}/{}".format(host,\
                                                                              config.db_port,\
                                                                              config.db_name))
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()