import configparser
from lib import aws_config, aws

# CONFIG
"""config_path = '../dwh.cfg'
config = configparser.ConfigParser()
config.read(config_path)"""

config_path = "../dwh.cfg"
config = aws_config(config_path)

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users CASCADE"
song_table_drop = "DROP TABLE IF EXISTS songs CASCADE"
artist_table_drop = "DROP TABLE IF EXISTS artist CASCADE"
time_table_drop = "DROP TABLE IF EXISTS time CASCADE"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events(
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
    )
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs(
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
    )
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id INT IDENTITY(1,1),
    start_time BIGINT, 
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
    ) 
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    gender VARCHAR,
    level VARCHAR,
    PRIMARY KEY (user_id)
    )
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
    song_id VARCHAR,
    title VARCHAR,
    artist_id VARCHAR,
    year INT,
    duration FLOAT,
    PRIMARY KEY (song_id)
    )
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR,
    artist_name VARCHAR,
    artist_location VARCHAR,
    artist_latitude INT,
    artist_longitude INT,
    PRIMARY KEY (artist_id)
    )
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
    start_time BIGINT,
    hour INT,
    day INT,
    week INT,
    month INT,
    year INT,
    weekday INT,
    PRIMARY KEY (start_time)
    )
""")

# STAGING TABLES

aws_clients = aws(config)
role_arn_dwhS3 = aws_clients.iam.get_role(RoleName=config.iam_role_name)['Role']['Arn']

staging_events_copy = ("""
COPY staging_events 
FROM '{}' 
iam_role '{}' 
json '{}';
""").format(config.log_data, role_arn_dwhS3, config.log_jsonpath)
print(staging_events_copy)

staging_songs_copy = ("""
COPY staging_songs 
FROM '{}' 
iam_role '{}' 
json 'auto';
""").format(config.song_data, role_arn_dwhS3)

# FINAL TABLES

songplay_table_insert = ("""
""")

user_table_insert = ("""
INSERT INTO users (
    user_id,
    first_name,
    last_name,
    gender,
    level 
) SELECT
    userid,
    firstName,
    lastName,
    gender,
    level
FROM
    staging_events
WHERE
    userid IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (
    song_id,
    title,
    artist_id,
    year,
    duration 
) SELECT
    song_id,
    title,
    artist_id,
    year,
    duration
FROM
    staging_songs
""")

artist_table_insert = ("""
INSERT INTO artists (
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_longitude 
) SELECT
    artist_id, 
    artist_name, 
    artist_location, 
    artist_latitude, 
    artist_longitude
FROM
    staging_songs
""")

time_table_insert = ("""
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create]

drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]

copy_table_queries = [staging_songs_copy, staging_events_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
