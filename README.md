# Data Practice - by Jonathan De La Cruz

![WithBGDataPractice drawio](https://github.com/user-attachments/assets/76e4ce8b-7ebc-4a52-bd39-b266a25304ab)

This project is a system made with AWS that receives 2 types of data, files uploaded representing batch data, in the other hand real time data, in this case simulated in python. These 2 types of data get stored in an S3 Bucket, are processed and stored in DynamoDB tables, finally the data is fetched and displayed on a report using Streamlit and Python. 

> [!TIP]
> The [Documentation](https://github.com/JonathanDeLaCruzEncora/aws-data-practice/blob/main/documentation.pdf) is available with steps on how to reproduce this system.

> [!NOTE]
> An [example report](https://github.com/JonathanDeLaCruzEncora/aws-data-practice/blob/main/report/report.pdf) is available to see the end result.

## Explanations for folders and files

### Folders

- **eventbridge/** : <br>
  Stores the pattern needed to only gather notification of a certain folder in an s3 bucket

- **gluejobs/** : <br>Two files for the AWS Glue jobs to set up.

- **kinesisfirehose/** : <br> Stores the prefixes to store data in the s3 buckets.

- **lambda/** : <br> Stores the lambda function file.

- **policies/** : <br> It stores the trust policies, and the main policy for an IAM role.

- **report/** : <br> An example report in pdf format.

- **sample_data/** : <br> 4 files to upload as batch data and a python file to separate the data yourself.

### Files

- **boto3_utils.py** : <br> File with the function to fetch the data from a DynamoDB table.

- **report.py** : <br> Python file with streamlit program to generate a report on data from DynamoDB.

- **send_data_to_kinesis.py** : <br> Python program to simulate real time data.



