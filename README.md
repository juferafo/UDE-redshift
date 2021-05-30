# UDE-redshift

Cloud-based Data Warehouses (DWH) are widely used by companies as part of their underlying infrastructure to process and analyze raw data. Cloud providers like Amazon Web Services (AWS) provide products, like [Redshift](https://aws.amazon.com/redshift/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc), where data engineers can implement and manage a data playground. Such playground is build with the goal of organizing the meaningful information contained in the raw data. DWHs are key for analysts to execute queries against the tables that conform the database and, in this way, to derive insights from their result.

The goal of this repository is to build a cloud-based DWHs. For this purpose we will make use of Amazon Redshift. We will design a data pipeline that will process and organize raw data into a star-shaped schema. The work presented here can be thought as an extension of the use-case presented in [this repository](https://github.com/juferafo/UDE-postgres).

This repository is organized as follows: 

### Project raw datasets

We are going to ilustrate the work presented here with the following use-case: let's assume that we are working for a music streaming startup and we are interested in migrating our on-premise data to the cloud. Our work is to design the DWH's structure of and to the implement this migration programatically. The raw data is divided into two large datasets: the song dataset and the log dataset.

#### Song dataset

The song dataset is a subset of the [Million Song Dataset](http://millionsongdataset.com/). It contains information about the songs available in the streaming app like artist_id, song_id, title, duration, etc... Each entry (row) of this dataset is written as a JSON file that are organized in folders with the following structure:

```
./data/song_data/
└── A
    ├── A
    │   ├── A
    │   ├── B
    │   └── C
    └── B
        ├── A
        ├── B
        └── C
```

Below you can find an example of the information contained in the song data file `song_data/A/A/B/TRAABJL12903CDCF1A.json`.

```
{
    "num_songs": 1, 
    "artist_id": "ARJIE2Y1187B994AB7", 
    "artist_latitude": null,
    "artist_longitude": null,
    "artist_location": "",
    "artist_name": "Line Renaud",
    "song_id": "SOUPIRU12A6D4FA1E1",
    "title": "Der Kleine Dompfaff",
    "duration": 152.92036,
    "year": 0
}
```

#### Log dataset

The log dataset contains information about the usage of the application by the customers. This dataset is build from the event simulator [eventsim](https://github.com/Interana/eventsim) and, like the song dataset, the data is stored in JSON files. Below you can find the different fields present in this dataset. As one can expect, from these logs one can derive user-based insights that are key when bussiness deciscissions are made.   

```
{
  artist TEXT,
  auth TEXT,
  firstName TEXT,
  gender TEXT,
  itemInSession INT,
  lastName TEXT,
  length DOUBLE,
  level TEXT,
  location TEXT,
  method TEXT,
  page TEXT,
  registration DOUBLE,
  sessionId INT,
  song TEXT,
  status INT,
  ts FLOAT,
  userId INT
}
```

For convenience and since this project is based on cloud technologies the aforementioned datasets were placed in a [S3 bucket](https://aws.amazon.com/s3/). Amazon S3 is an object storage service that allows to store high volume data in a way that this one is cost effective, highly available, secure and easy to retrieve from other AWS services like S3. Below you can find the S3 links

* Song data: `s3://udacity-dend/song_data`
* Log data: `s3://udacity-dend/log_data`

### Data Warehouse structure

As mentioned earlier, our goal is to bring data located in S3 into the DWH. Widely speaking, we can divide the structure of our system in two areas: the staging area and the DW area.

#### Staging area

The Staging area is the place where the input or so-called raw data is located. In our case the stagins area will consist on two tables: `staging_songs` and `staging_events` that will encapsulate the information present in the S3 buckets `s3://udacity-dend/song_data` and `s3://udacity-dend/log_data` respectively. In this area the data is in its original format and, as one can imagine, it is necessary to implement an Extract-Transform-Load (ETL) pipeline to put the data into the desired shape and within the target place. In the next section, a detailed description of the applied ETL procedure is provided. Below you can find the internal schema of each table present in the staging area.

##### `staging_songs` fact table

```
artist_id VARCHAR,
artist_latitude FLOAT,
artist_location VARCHAR,
artist_longitude FLOAT,
artist_name VARCHAR,
duration FLOAT,
num_songs INT,
song_id VARCHAR,
title VARCHAR,
year INT
```

##### `staging_events` dimension table

```
artist VARCHAR,
auth VARCHAR,
firstName VARCHAR,
gender VARCHAR,
itemInSession INT,
lastName VARCHAR,
length FLOAT,
level VARCHAR,
location VARCHAR,
method VARCHAR,
page VARCHAR,
registration BIGINT,
sessionId INT,
song VARCHAR,
status INT,
ts BIGINT,
userAgent VARCHAR,
userId INT
```

#### Reporting area

The reporting area is the final location of the input data and it is the place where the Analyticts team will work. The song and log data will be organized in the so-called [normalized form](https://en.wikipedia.org/wiki/Database_normalization) with the shape of a [star-schema](https://www.guru99.com/star-snowflake-data-warehousing.html). A database designed with a star-shaped schema is built around the a fact-table that in our case contains information of the songs played by the customers. The fact table will connect to the dimension tables by means of foreign keys. The dimension tables are used to store descriptive information like, for example, the song, artist or user details. 
Below you can find the internal schema of each table present in the reporting area.

##### `songplays` fact table

```
songplay_id INT IDENTITY(1,1),
start_time TIMESTAMP, 
user_id INT, 
level VARCHAR, 
song_id VARCHAR, 
artist_id VARCHAR, 
session_id INT, 
location VARCHAR, 
user_agent VARCHAR,
PRIMARY KEY (songplay_id),
FOREIGN KEY (user_id) REFERENCES users(user_id),
FOREIGN KEY (song_id) REFERENCES songs(song_id),
FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
FOREIGN KEY (start_time) REFERENCES time(start_time)
```

##### `artist` dimension table

```
artist_id VARCHAR,
artist_name VARCHAR,
artist_location VARCHAR,
artist_latitude INT,
artist_longitude INT,
PRIMARY KEY (artist_id)
```

#### `song` dimension table

```
song_id VARCHAR,
title VARCHAR,
artist_id VARCHAR,
year INT,
duration FLOAT,
PRIMARY KEY (song_id)
```

##### `time` dimension table

```
start_time TIMESTAMP,
hour INT,
day INT,
week INT,
month INT,
year INT,
weekday INT,
PRIMARY KEY (start_time)
```

##### `user` dimension table

```
user_id INT,
first_name VARCHAR,
last_name VARCHAR,
gender VARCHAR,
level VARCHAR,
PRIMARY KEY (user_id)
```

### Extract-Transform-Load (ETL) pipeline

An ETL pipeline is a programatic procedure used by data engineers to retrieve data from a particular source (extract), to modify its information in order to meed certain  validation requirements (transform) and to save it into a database or another storage service (load). For our use-case we need also create the tables present in the DW area so the load step is executed successfully. 

The ETL pipeline presented in this repository was coded using Python 3. At the end of this README you can find the requirements to run the Python scripts. The different steps of the ETL process are explained in the following subsections.

#### Creation of AWS resources

In order to work with Redshift it is required first to have a AWS account and to create the resources that we are going to use. This is: a redshift cluster with the role required to retrieve data from S3. The script `./aws_setup.py` was created for this purpose using the AWS Python Library `boto3` and, in addition, some custom methods that can be found in `./lib.py`. 

The creation/deletion and ETL are automatic and retreive sensitive data from the configuration file `./dwh.cfg`. The parameters present in this file are required for the correct execution of the scripts. Below you can find the parameters required in the configuration file:

```
[CLUSTER_PROPERTIES]
DB_NAME=sparkify
DB_USER=***EDITED***
DB_PASSWORD=***EDITED***
DB_PORT=***EDITED***
DWH_CLUSTER_TYPE=multi-node
DWH_NUM_NODES=4
DWH_NODE_TYPE=dc2.large
DWH_CLUSTER_IDENTIFIER=dwhCluster
REGION_NAME=us-west-2

[IAM_ROLE]
ARN=arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
IAM_ROLE_NAME=dwhRole

[S3]
LOG_DATA=s3://udacity-dend/log_data
LOG_JSONPATH=s3://udacity-dend/log_json_path.json
SONG_DATA=s3://udacity-dend/song_data/A/A/A

[AWS_SECURITY]
KEY=***EDITED***
SECRET=***EDITED***
```

Running the script `aws_setup.py` will print the following information on the screen:

```
$ python aws_setup.py
IAM role dwhRole created
IAM policy arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess attached to the role dwhRole

Redshift cluster created with properties:

ClusterType: multi-node
NodeType: dc2.large
NumberOfNodes: 4
DBName : sparkify
ClusterIdentifier: dwhCluster
IamRoles: arn:aws:iam::273305144712:role/dwhRole
```

#### Generation of the DW star-schema

#### Extract



#### Transform

#### Load

### Sample queries

### Cleanup

```
$ python ./aws_cleanup.py 
IAM policy arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess detached from the role dwhRole
IAM role dwhRole deleted

Redshift cluster dwhCluster deleted
```

## Requirements

1. [`boto3`](https://aws.amazon.com/en/sdk-for-python/)
2. [`psycopg2`](https://www.psycopg.org/docs/)
3. [`configparser`](https://docs.python.org/3/library/configparser.html)
