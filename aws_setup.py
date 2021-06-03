"""
This script can be used to create a redshift cluster 
with an iam role attached that makes possible to read data from S3.
The AWS-related parameters are read from the configuration file ./dwh.cfg
"""

import boto3
import configparser
import json

from lib import aws_config, aws
from lib import iamS3, create_redshift
from lib import cleanup_iam, cleanup_redshift
    
# Reading configuration parameters
config_path = './dwh.cfg'
# custom helper method defined in ./lib.py
config = aws_config(config_path)

# aws object with iam and redshift clients generated from the config paramenters
aws_clients = aws(config)

# attaching the "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" policy to the redshift role
# creating a Redshift cluster with such a role will allow it to read data from S3
role_arn = iamS3(aws_clients.iam, config)
create_redshift(aws_clients.redshift, config, role_arn)

# Cleanup resources. 
# Careful! The resources created above will be deleted!
# cleanup_iam(aws_clients.iam, config)
# cleanup_redshift(aws_clients.redshift, config)
