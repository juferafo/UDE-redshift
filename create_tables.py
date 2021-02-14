import configparser
import psycopg2
import boto3
from lib import aws_config, aws
from lib import redshift_connection
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
    config_path = "../dwh.cfg"
    conn, cur, aws_clients, config = redshift_connection(config_path)
    
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()

    
if __name__ == "__main__":
    main()