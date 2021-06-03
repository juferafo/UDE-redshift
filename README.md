# UDE-redshift

Cloud-based Data Warehouses (DWHs) are widely used by companies as part of their computational infrastructure. Together with programmatic procedures they are used to process and analyse raw data. Cloud providers like Amazon Web Services (AWS) provide products, like [Redshift](https://aws.amazon.com/redshift/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc), that data engineers and use as a data playground. Such environment is built with the ultimate goal of extracting meaningful information from the raw data.

The goal of this repository is to build a cloud-based DWH. For this purpose we will make use of Amazon Redshift. We will design a data pipeline that will process and organize raw data into a star-shaped schema. The work presented here can be thought as an extension of the use-case presented in [this repository](https://github.com/juferafo/UDE-postgres).

### Project datasets

We are going to illustrate the above-mentioned task with the following use-case: let's assume that we are working for a music streaming start-up and we are interested in migrating our on-premise data to the cloud. Our work is to design the DWH's structure and to implement this migration in an automatized way. As explained below, the raw data is divided into two large datasets: the song dataset and the log dataset.

#### Song dataset

The song dataset is a subset of the [Million Song Dataset](http://millionsongdataset.com/). It contains information about the songs available in the streaming app like the artist ID, song ID, title, duration, etc... Each entry (row) of this dataset is written as a JSON file that are organized in folders with the following structure:

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

Below you can find an example of a song data file.

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

The log dataset contains information about the app usage by the customers. This dataset is build from the simulator of events [eventsim](https://github.com/Interana/eventsim) and, like the song dataset, the information is stored in JSON files. Below you can find the different fields present in this dataset. As one can expect, from these logs one can derive user-based insights that are key for business decisions.

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

For convenience and since this project is based on cloud technologies the aforementioned datasets were placed in a [S3 bucket](https://aws.amazon.com/s3/). Amazon S3 is an object storage service that allows storing high volume data in a cost effective, highly available, secure and easy to retrieve way. Below you can find the links to the S3 buckets that host the raw data.

* Song data: `s3://udacity-dend/song_data`
* Log data: `s3://udacity-dend/log_data`

### Data Warehouse structure

As mentioned earlier, our goal is to bring the data located in S3 into the DWH. Widely speaking, we can divide the structure of the DWH in two areas: the Staging area and the Reporting area.

#### Staging area

The Staging area is the place where the input or raw data will be placed within the DWH. In our case, the Staging area will consist on two tables: `staging_songs` and `staging_events`. These tables will encapsulate the information present in the S3 buckets `s3://udacity-dend/song_data` and `s3://udacity-dend/log_data` as is. As one can imagine, it is necessary to implement an Extract-Transform-Load (ETL) pipeline to put the data into the desired shape. In the next section, a detailed description of the ETL procedure is provided. Below you can find the internal schema of each table present in the staging area.

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

The Reporting area is the final location of the data within the DWH. The song and log data will be organized in the so-called [normalized form](https://en.wikipedia.org/wiki/Database_normalization) with the shape of a [star-schema](https://www.guru99.com/star-snowflake-data-warehousing.html). A database designed with a star-shaped schema is built around the fact table that, in our case, contains information of the songs played by the customers. The fact table will connect to the dimension tables by means of foreign keys. The dimension tables are used to store descriptive information like, for example, the song, artist or user details. 
Below you can find the internal schema of each table present in the Reporting area.

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

An ETL pipeline is a programmatic procedure used by data engineers to Extract data from a particular source, to Transform its information in order to meet certain validation requirements and to Load it into a database or another service. In our use-case we need to retrieve the raw data present in the Staging area and ensure that it has the adequate format before ingesting this information into the reporting area. The ETL pipeline presented in this repository was coded using Python 3 and can be found in the script `./etl.py`. In the below subsections we provide a description of the steps needed to execute the ETL pipeline successfully.

#### Creation of AWS resources

In order to work with Redshift it is necessary to create a Redshift cluster with permissions to retrieve data from S3. The script `./aws_setup.py` was created to deploy this infrastructure in AWS. For this purpose, the AWS Library `boto3` and custom methods that can be found in the code `./lib.py` were used. The scripts included in this repository are coded to read the configuration parameters stored in `./dwh.cfg`. Such file contains information about the Redshift cluster (number of nodes, region, etc...), the database (user, password, port, etc...) and authentication credentials. 

Running the script `./aws_setup.py` will print the following information on the screen:

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

Please wait until the status of the cluster appears as `Available` in the Redshift web-UI before moving to the next section.

#### Creation of the DW tables

Once the cluster is ready, we will use the code `./create_tables.py` to generate the tables present in both Staging and Report areas. The creation of these tables is done by means of SQL [CREATE](https://www.postgresql.org/docs/10/sql-createtable.html) statements that can be inspected in the script `./sql_queries.py`. As a measure of caution, before any CREATE operation is carried out, a [DROP TABLE](https://www.postgresql.org/docs/10/sql-droptable.html) one is executed. The script `./create_tables.py` can be used to reset the DWH since it will remove all the data present in it.

#### ETL pipeline

The ETL pipeline is encapsulated in the script `./etl.py`. As mentioned earlier, the goal of this script is two-fold:

1. To bring the raw data located in S3 into the Staging area.
2. To re-organize the raw data into a star-shaped schema.

Similarly to the previous scripts, `./etl.py` makes use of the methods written in `./lib.py` to automatize certain tasks like, for example, reading configuration data from `./dwh.cfg`. The `main` method of  `./etl.py` is divided in two parts and, conceptually, it can be reduced to two independent methods:

1. `load_staging_tables` that carries out the task of loading the data from S3 to Redshift. The `psycopg2` library was employed in order to establish a connection to the DWH. For efficiency, the command [COPY](https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html) was used to ingest the data.
2. `insert_tables` that makes use of the SQL [INSERT](https://www.postgresql.org/docs/13/sql-insert.html) statements present in `./sql_queries.py` to distribute the raw data in the Reporting area.

Once the ETL procedure has been executed we will see the data loaded in both areas of the DWH. From the Redshift web-UI it is possible to execute queries against the DWH.

### Cleanup

The script `./aws_cleanup.py`is available for the users to tear down the AWS resources to avoid unwanted charges.

## Requirements

1. [`boto3`](https://aws.amazon.com/en/sdk-for-python/)
2. [`psycopg2`](https://www.psycopg.org/docs/)
3. [`configparser`](https://docs.python.org/3/library/configparser.html)
