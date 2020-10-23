import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
import requests
import time
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    message_body = (event['Records'][0]["body"])
    message_body = message_body.replace("\'", "\"")
    print(message_body)

    res = json.loads(message_body)
    cuisine = res['Cuisine']
    print(cuisine)
    credentials = boto3.Session().get_credentials()
    region = 'us-east-1'
    service = 'es'
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'search-restaurants-luryqvoc4k7tsv7e5fks42zhyi.us-east-1.es.amazonaws.com'

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
    sqs = boto3.resource('dynamodb')
    table_name = sqs.Table('yelp-restaurants')

    k = es.search(index="restaurants", doc_type="_doc", body={"query": {"match": {"cusine": cuisine}}}, size=5)
    l = json.dumps(k)

    id = []
    ans = []
    for i in (k['hits']['hits']):
        print(i['_id'])
        response = table_name.get_item(
            Key={
                '_id': i['_id'],
            }
        )
        ans.append(response)
    print(ans)
    message = "Hello! Here are my " + str(res["Cuisine"]) + " restaurant suggestions for " + str(
        res["No_of_people"]) + " people, for " + str(res["Date"]) + ":" + "\n"
    for i in range(0, 3):
        response = ans[i]
        msg = str(i + 1) + ")" + str(response["Item"]["name"]) + " located at " + str(response["Item"]["address"])
        message = message + msg + "\n"
    message = message + "Enjoy your meal!"
    print(message)
    arn = "arn:aws:sns:us-east-1:039880994656:chatbot-msg"
    client = boto3.client('sns', 'us-east-1')
    status1 = client.publish(Message=message, MessageStructure='string', PhoneNumber=res["Phone_Number"])

    return
    {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }