import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from decimal import *
import time

with open('data.json') as json_file:
    data = json.load(json_file)

for i in data['businesses']:
    print(i['id'], i['name'], i['location'], i['coordinates'], i['review_count'], i['rating'],
          i['location']['zip_code'])

for i in data['businesses']:
    l = []
    for j in i['categories']:
        l.append(j['alias'])
    record = {"name": i['name'], "cusine": l}

    y = json.dumps(record)

credentials = boto3.Session(aws_access_key_id='xxxx',                          # aws account credentials
                            aws_secret_access_key='xxxx').get_credentials()

region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = 'xxx'   # elastic search url
print(awsauth)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id='xxxx',
                          aws_secret_access_key='xxxx')
table = dynamodb.Table('yelp-restaurants')

for i in data['businesses']:
    l = []
    for j in i['categories']:
        l.append(j['alias'])
    record = {"name": i['name'], "cusine": l}
    y = json.dumps(record)

    rec = {"_id": i['id'], "name": i['name'],
           "address": i['location']['address1'], "coordinates_la": Decimal(str(i['coordinates']['latitude'])),
           "coordinates_lo": Decimal(str(i['coordinates']['longitude'])),
           "review_count": i['review_count'], "rating": Decimal(str(i['rating'])),
           "zip_code": i['location']['zip_code'], "inserted_at": str(time.asctime(time.localtime(time.time())))}

    response = table.put_item(Item=rec)
    es.index(index="restaurants", doc_type="_doc", id=i['id'], body=y)





