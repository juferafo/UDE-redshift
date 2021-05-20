"""
This script contains helper classes and methods to automatize the creation of
the needed resources to run this repository
"""

import boto3
import configparser
import json
import psycopg2

class aws_config(str):
    """
    This class can be used to gather different metadata and other relevant information stored in the configuration 
    file dwh.cfg into a single object.
    
    Attributes:
        key: AWS secutiry key
        secret: AWS secret key
        region_name: name of the region where the Redshift cluster is located
        dwh_cluster_type: Redshift cluster type
        dwh_num_nodes: number of nodes
        dwh_node_type: node configuration type
        dwh_cluster_identifier: cluster identifier
        db_name: database name
        db_user: database user
        db_password: database password
        db_port: database connection port
        iam_arn: IAM ARN role 
        iam_role_name: IAM ARN role name
        log_data: S3 log (or events) data path 
        log_jsonpath: JSON path of log data used in the COPY query
        song_data: S3 sonce data path 
    """

    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read_file(open(config_path))
        
        # AWS_SECURITY
        self.key = config.get('AWS_SECURITY','KEY')
        self.secret = config.get('AWS_SECURITY','SECRET')

        # CLUSTER_PROPERTIES
        self.region_name            = config.get('CLUSTER_PROPERTIES','REGION_NAME')
        self.dwh_cluster_type       = config.get("CLUSTER_PROPERTIES","DWH_CLUSTER_TYPE")
        self.dwh_num_nodes          = config.get("CLUSTER_PROPERTIES","DWH_NUM_NODES")
        self.dwh_node_type          = config.get("CLUSTER_PROPERTIES","DWH_NODE_TYPE")
        self.dwh_cluster_identifier = config.get("CLUSTER_PROPERTIES","DWH_CLUSTER_IDENTIFIER")
        self.db_name                = config.get("CLUSTER_PROPERTIES","DB_NAME")
        self.db_user                = config.get("CLUSTER_PROPERTIES","DB_USER")
        self.db_password            = config.get("CLUSTER_PROPERTIES","DB_PASSWORD")
        self.db_port                = config.get("CLUSTER_PROPERTIES","DB_PORT")

        # IAM_ROLE
        self.iam_arn       = config.get('IAM_ROLE','ARN')
        self.iam_role_name = config.get('IAM_ROLE','IAM_ROLE_NAME')
        
        # S3
        self.log_data     = config.get('S3','LOG_DATA')
        self.log_jsonpath = config.get('S3','LOG_JSONPATH')
        self.song_data    = config.get('S3','SONG_DATA')

        
class aws(aws_config):
    """
    This class is designed to build objects that act as entry point of the IAM, Redshift and S3 functionality.
    For this purpose the different attributes correspond to the boto3 clients of iam, redshift and s3.
    
    Attributes:
        iam: boto3 IAM client
        redshift: boto3 Redshift client
        s3: boto3 S3 resource
    """
    
    def __init__(self, aws_config):
        
        aws.iam = boto3.client('iam',\
                               region_name=aws_config.region_name,\
                               aws_access_key_id=aws_config.key,\
                               aws_secret_access_key=aws_config.secret\
                              )

        aws.redshift = boto3.client('redshift',\
                                    region_name=aws_config.region_name,\
                                    aws_access_key_id=aws_config.key,\
                                    aws_secret_access_key=aws_config.secret\
                                   )
        
        aws.s3 = boto3.resource('s3',\
                                region_name=aws_config.region_name,\
                                aws_access_key_id=aws_config.key,\
                                aws_secret_access_key=aws_config.secret\
                               )
        

def iamS3(iam, config):
    """
    This method is used to create an iam role that allows Redshift to read data from S3 buckets.
    
    Args:
        iam (botocore.client.IAM): boto3 IAM object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
        
    Returns:
        rolearn_dwhS3 (str)
    """
    
    iamrole_dwhS3 = iam.create_role(
        Path='/',
        RoleName=config.iam_role_name,
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
                            'Effect': 'Allow',
                            'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'})
    )    
    
    print("IAM role {} created".format(config.iam_role_name))
    
    iam.attach_role_policy(
        RoleName=config.iam_role_name,
        PolicyArn=config.iam_arn
    )['ResponseMetadata']['HTTPStatusCode']
    
    print("IAM policy {} attached to the role {}\n".format(config.iam_arn, config.iam_role_name))
    
    rolearn_dwhS3 = iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']
    
    return rolearn_dwhS3


def create_redshift(redshift, config, role_arn):
    """
    This method is used to create a Redshift cluster.
    
    Args:
        redshift (botocore.client.Redshift): boto3 Redshift object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
        role_arn (str): ARN role that will be attached to the Redshift cluster
    """
    
    response = redshift.create_cluster(     
        ClusterType       = config.dwh_cluster_type,
        NodeType          = config.dwh_node_type,
        NumberOfNodes     = int(config.dwh_num_nodes),
        DBName            = config.db_name,
        ClusterIdentifier = config.dwh_cluster_identifier,
        MasterUsername    = config.db_user,
        MasterUserPassword= config.db_password,
        IamRoles          = [role_arn]  
    )
    
    print("Redshift cluster created with properties:")
    
    print("ClusterType: {}".format(config.dwh_cluster_type))
    print("NodeType: {}".format(config.dwh_node_type))
    print("NumberOfNodes: {}".format(config.dwh_num_nodes))
    print("DBName : {}".format(config.db_name))
    print("ClusterIdentifier: {}".format(config.dwh_cluster_identifier))
    # Commented for security reasons
    #print("MasterUsername : {}".format(config.db_user)
    #print("MasterUserPassword : {}".format(config.db_password)
    print("IamRoles: {}\n".format(role_arn))
    
    
def cleanup_iam(iam, config):
    """
    This method deletes the iam role that allows Redshift to read the staging log and song data from S3
    
    Args:
        iam (botocore.client.IAM): boto3 IAM object 
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
    """
    
    iam.detach_role_policy(RoleName=config.iam_role_name, PolicyArn=config.iam_arn)
    print("IAM policy {} detached from the role {}".format(config.iam_arn, config.iam_role_name))
    iam.delete_role(RoleName=config.iam_role_name)
    print("IAM role {} deleted\n".format(config.iam_role_name))

    
def cleanup_redshift(redshift, config):
    """
    This method deletes the redshift cluster.
    
    Args:
        redshift (botocore.client.Redshift): boto3 Redshift object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
    """
    
    redshift.delete_cluster(ClusterIdentifier=config.dwh_cluster_identifier, SkipFinalClusterSnapshot=True)
    print("Redshift cluster {} deleted".format(config.dwh_cluster_identifier))
    

def redshift_connection(redshift, config):
    """
    This method can be used to connect to the Redshift clusted. 
    It will make use of the method lib.aws_config to read the ClusterIdentifier, database name, 
    database uer, database pasword and database port from the configuration file to generate the connection string.
    It returns the psycopg2 cursor and connection to the Redshift database.
    
    Args:
        redshift (botocore.client.Redshift): boto3 Redshift object
        config (lib.aws_config): object that contains metadata information about the DWH setup (.cfg file)
    
    Returns:
        cur (psycopg2.extensions.cursor)
        conn (psycopg2.extensions.connection)
    """
        
    cluster_identifier = config.dwh_cluster_identifier
    redshift_properties = redshift.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
    
    host = redshift_properties['Endpoint']['Address']
    connection_string = "host={} dbname={} user={} password={} port={}".format(host,\
                                                                               config.db_name,\
                                                                               config.db_user,\
                                                                               config.db_password,\
                                                                               config.db_port)
    # Careful! This will print a password on the screen!
    # Commented for security reasons
    #print(connection_string)
    
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    
    return conn, cur