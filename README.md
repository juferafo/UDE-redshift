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

Below you can find an example of the data corresponding to the song ./data/song_data/A/A/A/TRAAAAW128F429D538.json

```
{
   "num_songs":1,
   "artist_id":"ARD7TVE1187B99BFB1",
   "artist_latitude":null,
   "artist_longitude":null,
   "artist_location":"California - LA",
   "artist_name":"Casual",
   "song_id":"SOMZWCG12A8C13C480",
   "title":"I Didn't Mean To",
   "duration":218.93179,
   "year":0
}
```

#### Log dataset

The log dataset

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

### Data Warehouse structure

#### Staging area

#### Data Warehouse schema

```
songplay_id SERIAL PRIMARY KEY,
start_time BIGINT, 
user_id INT, 
level VARCHAR, 
song_id VARCHAR, 
artist_id VARCHAR, 
session_id INT, 
location VARCHAR, 
user_agent VARCHAR
```

```
user_id INT PRIMARY KEY,
first_name VARCHAR,
last_name VARCHAR,
gender VARCHAR,
level VARCHAR
```

```
song_id VARCHAR PRIMARY KEY,
title VARCHAR,
artist_id VARCHAR,
year INT,
duration FLOAT
```

```
artist_id VARCHAR PRIMARY KEY,
artist_name VARCHAR,
artist_location VARCHAR,
artist_latitude INT,
artist_longitude INT
```

```
start_time BIGINT PRIMARY KEY,
hour INT,
day INT,
week INT,
month INT,
year INT,
weekday INT




### ETL pipeline

### 
