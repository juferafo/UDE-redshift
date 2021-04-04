"""
This script can be used to cleanup the IAM and Redshift resources created
"""


import boto3
import configparser

from lib import aws_config, aws
from lib import cleanup_iam, cleanup_redshift
    
# Reading configuration parameters
config_path = '../dwh.cfg'
config = aws_config(config_path)

# aws object with iam and redshift clients generated from the config paramenters
aws_clients = aws(config)

# Cleanup resources
cleanup_iam(aws_clients.iam, config)
cleanup_redshift(aws_clients.redshift, config)