The Dining Concierge chatbot is a microservice-driven web application where the chatbot sends restaurant suggestions given a set of preferences that you provide to the chatbot through conversation.

# AWS Services Used

# Implementation
<ol>
  <li> Build and deploy the frontend of the application in an AWS S3 bucket</li>

  <li> Build the API for the application</li>
  <ul>
    <li>a. Used API Gateway to setup the API using Swagger</li>
    <li>b. Create a Lambda function (LF0) that performs the chat operation</li>
  </ul>
  
  <li>3. Build a Dining Concierge chatbot using Amazon Lex.</li>
  <ul>

    <li>a. Created a bot using the Amazon Lex service.</li>
    <li> Created a Lambda function (LF1) as a code hook for Lex, which essentially entails the invocation of your Lambda before Lex responds to any of your requests -- this helps to manipulate and validate parameters as well as format the bot’s responses.</li>
    <li>c. The bot used three intents:</li>

● GreetingIntent : response such as **“Hi there, how can I help?”**

● ThankYouIntent : **"Thank you"**

● DiningSuggestionsIntent

  
2/7 iii. For the DiningSuggestionsIntent, the chat bot collect at least one of the following pieces of information from the user, through conversation:

● Location

● Cuisine

● Dining Time

● Number of people

● Phone number

Based on the parameters collected from the user, the information is then pushed to an SQS queue (Q1).

● Then a confirmation is send to the user that the user will receive the suggestions over SMS.

4. Integrate the Lex chatbot into your chat API

a. Use the AWS SDK to call your Lex chatbot from the API Lambda (LF0).

b. When the API receives a request:
    1. extract the text message from the API request, 
    2. send it to your Lex chatbot, 
    3. wait for the response, 
    4. send back the response from Lex as the API response.

5. Used the Yelp API to collect 5,000+ random restaurants from Manhattan.


ii. DynamoDB (a noSQL database)

● Create a DynamoDB table and named “yelp-restaurants”

● Store the restaurants you scrape, in DynamoDB because some restaurants might have more or less fields than others, which makes DynamoDB ideal for storing this data

● Only Stored the information that are necessary for your recommendation like Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code

6. Created an ElasticSearch instance using the AWS ElasticSearch Service.

○ Created an ElasticSearch index called “restaurants” 
    ○ Create an ElasticSearch type under the index “restaurants” called “Restaurant” 
    ○ Stored the RestaurantID and Cuisine for each restaurant scraped in ElasticSearch under the “restaurants” index, where each entry has a “Restaurant” data type.

7. Build a suggestions module, that is decoupled from the Lex chatbot.

a. Create a new Lambda function (LF2) that acts as a queue worker.

Whenever it is invoked it 
    1. pulls a message from the SQS queue (Q1), 
    2. gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB, 
    3. formats them 
    4. sends them over text message to the phone number included in the SQS message, using SNS

i. Use the DynamoDB table “yelp-restaurants” (which you created from Step 1) to fetch more information about the restaurants (restaurant name, address, etc.), since the restaurants stored in ElasticSearch will have only a small subset of fields from each restaurant.


b. Set up a CloudWatch event trigger that runs every minute and invokes the Lambda function as a result. This automates the queue worker Lambda to poll and process suggestion requests on its own.

In summary, based on a conversation with the customer, your LEX chatbot will identify the customer’s preferred ‘cuisine’. You will search through ElasticSearch to get random suggestions of restaurant IDs with this cuisine. At this point, you would also need to query the DynamoDB table with these restaurant IDs to find more information about the restaurants you want to suggest to your customers like name and address of the restaurant.
