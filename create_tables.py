import configparser
import psycopg2
import boto3
from lib import aws_config, aws
from lib import redshift_connection
from sql_queries import create_table_queries, drop_table_queries

def drop_tables(cur, conn):
    """
    This method is used to drop all the tables in the database.
    To this end, the DROP-like queries included in the parameter drop_table_queries are executed.
    
    Args:
        cur (psycopg2.extensions.cursor): psycopg2 cursor object used to run queries against a database
        conn (psycopg2.extensions.connection): psycopg2 connection object
    """
    
    print("\nDropping tables\n")
    for query in drop_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    This method is used to create all the tables in the database.
    To this end, the CREATE-like queries included in the parameter create_table_queries are executed.
    
    Args:
        cur (psycopg2.extensions.cursor): psycopg2 cursor object used to run queries against a database
        conn (psycopg2.extensions.connection): psycopg2 connection object
    """
    
    print("\nCreating tables")
    for query in create_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()
        

def main():
    # To be done by the developer/user of this code: 
    # Edit the configuration file ./dwh.cfg according to your use-case
    # REMEMBER TO NOT EXPOSE LIVE TOKENS/PASSWORDS IN GIT/GITHUB!
    config_path = "../dwh.cfg"

    # the aws_config and aws classes can be found in the file lib.py
    config = aws_config(config_path)
    aws_clients = aws(config)
    
    redshift = aws_clients.redshift
    
    # The method redshift_connection is used to stablish a connection to the Redshift database
    conn, cur = redshift_connection(redshift, config)
    
    # Drop operation followed by the creation DDLs of the tables that will be hosted in the database
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()

    
if __name__ == "__main__":
    main()