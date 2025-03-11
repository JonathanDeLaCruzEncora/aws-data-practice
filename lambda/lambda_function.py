import json
import boto3
import base64
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ProcessedStream')

def lambda_handler(event, context):
    records = event.get('Records', [])

    # Window Metadata
    window_start = event.get('window', {}).get('start') or datetime.now(timezone.utc).isoformat()
    window_end = event.get('window', {}).get('end') or datetime.now(timezone.utc).isoformat()

    engagement_counts = {}

    for record in records:
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)
        
        post_id = data['post_id']
        engagement_type = data['engagement_type']

        key = (post_id, engagement_type)
        engagement_counts[key] = engagement_counts.get(key, 0) + 1

    # Update DynamoDB
    for (post_id, engagement_type), count in engagement_counts.items():
        partition_key = post_id
        sort_key = window_start

        engagement_attr_name = f'engagement_counts.{engagement_type}'

        table.update_item(
            Key={'post_id': partition_key, 'window_start': sort_key},
            UpdateExpression=f"SET #attr = if_not_exists(#attr, :start) + :count, window_end = :window_end",
            ExpressionAttributeNames={'#attr': engagement_attr_name},
            ExpressionAttributeValues={':count': count, ':start': 0, ':window_end': window_end}
        )

    print(f"Processed {len(records)} records in Tumbling Window [{window_start} - {window_end}].")
    return {'statusCode': 200, 'body': json.dumps({'message': 'Aggregation complete', 'records': len(records)})}