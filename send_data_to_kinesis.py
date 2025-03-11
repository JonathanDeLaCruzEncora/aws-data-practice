import glob
import json
import time
import boto3
import random
import pandas as pd
from datetime import datetime, timezone


# Settings for connection
kdsname = 'input_stream'
clientkinesis = boto3.client(
    'kinesis', 
    region_name='us-east-1', # Change to your region
    aws_access_key_id="YOUR ACCESS KEY",
    aws_secret_access_key="YOUR SECRET KEY"
)

# Insert all files in a directory called data
folder_path = "data/*.csv"
files = glob.glob(folder_path)
df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

types = ['Like', 'Comment', 'Share']

#Counter
i = 0

# REMEMBER TO STOP (CONTROL+C)
while True:
    randomIndex = random.randrange(df.shape[0])
    record = {
        'post_id': df.iloc[randomIndex,1],
        'engagement_type': random.choice(types),
        'user_id': f'{random.randrange(10000):04}',
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    response = clientkinesis.put_record(
        StreamName=kdsname,
        Data=json.dumps(record),
        PartitionKey=str(record['post_id'])
    )

    i += 1
    print(f"Total ingested: {i}, ReqID: {response['ResponseMetadata']['RequestId']}, HTTPStatusCode: {response['ResponseMetadata']['HTTPStatusCode']}")

    time.sleep(1)  # Wait 1 second