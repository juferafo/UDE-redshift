"""
This script contains a method that can be used to create a redshift cluster 
with an iam role attached that makes possible to read data from S3
"""

import boto3
import configparser
import json


class aws_config(str):

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
        self.iam_arn           = config.get('IAM_ROLE','ARN')
        self.iam_role_name = config.get('IAM_ROLE','IAM_ROLE_NAME')
        

class aws(aws_config):
    
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
        

def iamS3(iam, config):
    """
    This method creates a iam role that allows Redshift to read data from S3.
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
     
    iam.attach_role_policy(
        RoleName=config.iam_role_name,
        PolicyArn=config.iam_arn
    )['ResponseMetadata']['HTTPStatusCode']

    rolearn_dwhS3 = iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']
    
    return rolearn_dwhS3


def create_redshift(redshift, config, role_arn):
    """
    This method is used to create a Redshift cluster.
    
    Args:
        REGION_NAME (str):
        KEY (str):
        SECRET (str):
    """
    
    response = redshift.create_cluster(     
        ClusterType       =config.dwh_cluster_type,
        NodeType          =config.dwh_node_type,
        NumberOfNodes     =int(config.dwh_num_nodes),
        DBName            =config.db_name,
        ClusterIdentifier =config.dwh_cluster_identifier,
        MasterUsername    =config.db_user,
        MasterUserPassword=config.db_password,
        IamRoles          =[role_arn]  
    )

    
def cleanup_iam(iam, config):
    """
    This method deletes the iam role
    
    Args:
    
    """
    
    iam.detach_role_policy(RoleName=config.iam_role_name, PolicyArn=config.iam_arn)
    iam.delete_role(RoleName=config.iam_role_name)
    

def cleanup_redshift(redshift, config):
    """
    This method deletes the redshift cluster
    """
    
    redshift.delete_cluster(ClusterIdentifier=config.dwh_cluster_identifier, SkipFinalClusterSnapshot=True)
    
    
# Reading configuration parameters
config_path = '../dwh.cfg'
config = aws_config(config_path)

# aws object with iam and redshift clients generated from the config paramenters
aws_clients = aws(config)

# attaching the "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" policy to the redshift role
# creating a Redshift cluster with such a role will allow it to read data from S3
role_arn = iamS3(aws_clients.iam, config)

create_redshift(aws_clients.redshift, config, role_arn)

# Cleanup resources
#cleanup_iam(aws_clients.iam, config)
#cleanup_redshift(aws_clients.redshift, config)
