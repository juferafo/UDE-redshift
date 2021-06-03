"""
This script can be used to delete the IAM role and Redshift clusters
The AWS-related parameters are read from the configuration file ./dwh.cfg
"""

import boto3
import configparser

from lib import aws_config, aws
from lib import cleanup_iam, cleanup_redshift
    
# Reading configuration parameters
config_path = './dwh.cfg'
# custom helper method defined in ./lib.py
config = aws_config(config_path)

# aws object with iam and redshift clients generated from the config paramenters
aws_clients = aws(config)

# Cleanup resources
cleanup_iam(aws_clients.iam, config)
cleanup_redshift(aws_clients.redshift, config)