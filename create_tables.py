import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries
import boto3

def drop_tables(cur, conn):
    """
    This method is used to drop all the tables in the database.
    To this end, the queries included in the global parameter drop_table_queries are executed.
    """
    
    print("Dropping database tables\n")
    for query in drop_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    This method is used to create all the tables in the database.
    To this end, the queries included in the global parameter create_table_queries are executed.
    """
    
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()

def main():
    
    # configparser is used to read the parameters in ./dwh.cfg
    # Remember to edit ./dwh.cfg according to your needs!
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    print(*config['CLUSTER'].values())
    
    #conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    #cur = conn.cursor()

    #drop_tables(cur, conn)
    #create_tables(cur, conn)

    #conn.close()


if __name__ == "__main__":
    main()