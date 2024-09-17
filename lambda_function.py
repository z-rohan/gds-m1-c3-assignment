import pandas as pd
import boto3
from io import StringIO

def lambda_handler(event, context):
    # creating sns client
    sns_client = boto3.client('sns')

    # geting bucket and key from file arrival event trigger
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # publishing file arrival email 
    topic_arn = 'arn:aws:sns:us-east-1:699475915241:gds-m1-c3-assigment-sns'
    subscriber_arn = 'arn:aws:sns:us-east-1:699475915241:gds-m1-c3-assigment-sns:a8cb396b-e012-43c1-9db9-4f109542199a'
    sns_client.publish(TopicArn = topic_arn, TargetArn = subscriber_arn, Subject = f'File arrived', 
                       Message = f'File arrived in {bucket} with name as {key}')

    # creating s3 client 
    s3_client = boto3.client('s3')

    # reading the file into dataframe
    target_key = 'doordash-target-zn/' + key.split('/')[-1]
    response = s3_client.get_object(Bucket=bucket, Key=target_key)
    file_content = response["Body"].read().decode('utf-8')
    df = pd.read_json(StringIO(file_content))
    # filtering 
    df = df[df['status']=='delivered']
    # saving file to target folder
    df_json = df.to_json(orient = 'records', date_format = 'iso' )
    s3_client.put_object(Body = df_json,Bucket = bucket, Key = key)

    # File proccessed message delievering 
    sns_client.publish(TopicArn = topic_arn, TargetArn = subscriber_arn, Subject = f'File processed', 
                       Message = f'File arrived in {bucket} with name as {target_key}')