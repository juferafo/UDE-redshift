"""
This script contains a method that can be used to create a redshift cluster 
with an iam role attached that makes possible to read data from S3
"""

import boto3
import configparser
import json

def iamS3(iam, REGION_NAME, KEY, SECRET):
    """
    This method creates a iam role that allows Redshift to read data from S3.
    """
    
    iamrole_dwhS3 = iam.create_role(
        Path='/',
        RoleName='dwhRole',
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
               'Effect': 'Allow',
               'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'})
    )    
    
    
    iam.attach_role_policy(RoleName='dwhRole',
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                      )['ResponseMetadata']['HTTPStatusCode']

    rolearn_dwhS3 = iam.get_role(RoleName='dwhRole')['Role']['Arn']
    
    return rolearn_dwhS3


def create_redshift(redshift, KEY, SECRET, ROLE_ARN):
    """
    This method is used to create a Redshift cluster.
    
    Args:
        REGION_NAME (str):
        KEY (str):
        SECRET (str):
    """
    
    response = redshift.create_cluster(        
        #HW
        ClusterType=DWH_CLUSTER_TYPE,
        NodeType=DWH_NODE_TYPE,
        NumberOfNodes=int(DWH_NUM_NODES),

        #Identifiers & Credentials
        DBName=DWH_DB,
        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        MasterUsername=DWH_DB_USER,
        MasterUserPassword=DWH_DB_PASSWORD,
        
        #Roles (for s3 access)
        IamRoles=[roleArn]  
    )
    
    return None

    
def cleanup_iam(iam, ROLE_NAME, REGION_NAME, KEY, SECRET):
    """
    This method deletes the iam role provided.
    
    Args:
    
    """
    
    iam.detach_role_policy(RoleName=ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    iam.delete_role(RoleName=ROLE_NAME)
    
    
config = configparser.ConfigParser()
config.read_file(open('../dwh.cfg'))

# AWS_SECURITY
KEY = config.get('AWS_SECURITY','KEY')
SECRET = config.get('AWS_SECURITY','SECRET')

# CLUSTER_PROPERTIES
REGION_NAME = config.get('CLUSTER_PROPERTIES','REGION_NAME')

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("DWH","DWH_DB")
DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT               = config.get("DWH","DWH_PORT")

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")



[DWH] 
DWH_CLUSTER_TYPE=multi-node
DWH_NUM_NODES=4
DWH_NODE_TYPE=dc2.large

DWH_IAM_ROLE_NAME=dwhRole
DWH_CLUSTER_IDENTIFIER=dwhCluster
DWH_DB=dwh
DWH_DB_USER=dwhuser
DWH_DB_PASSWORD=Chou*7pou!!echo4
DWH_PORT=5439



# IAM_ROLE
DWH_IAM_ROLE_NAME = config.get('IAM_ROLE','DWH_IAM_ROLE_NAME')

# AWS clients

iam = boto3.client('iam',\
                   region_name=REGION_NAME,\
                   aws_access_key_id=KEY,\
                   aws_secret_access_key=SECRET\
                  )

redshift = boto3.client('redshift',\
                        region_name=REGION_NAME,\
                        aws_access_key_id=KEY,\
                        aws_secret_access_key=SECRET\
                       )

ROLE_ARN = iamS3(iam, REGION_NAME, KEY, SECRET)

create_redshift(redshift, REGION_NAME, KEY, SECRET, ROLE_ARN)

#cleanup_redshift()
cleanup_iam(iam, DWH_IAM_ROLE_NAME, REGION_NAME, KEY, SECRET)
