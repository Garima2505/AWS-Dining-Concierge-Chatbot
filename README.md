The Dining Concierge chatbot is a microservice-driven web application where the chatbot sends restaurant suggestions given a set of preferences that you provide to the chatbot through conversation.

# AWS Services Used
S3, AWS Lambda, API Gateway, Lex, SQS, SNS, Elastic Search, DynamoDB

# Architecture Diagram
![architecture](/images/architecture.png)

# Implementation
<ol>
  <li> Build and deployed the frontend of the application on AWS S3 bucket</li>
  <li> Build the API for the application</li>
    <ul>
        <li> Used API Gateway to setup the API using Swagger</li>
        <li> Created a Lambda function (LF0) that performs the chat operation</li>
    </ul>
  <li> Build a Dining Concierge chatbot using Amazon Lex.</li>
     <ul>
        <li> Created a bot using the Amazon Lex service.</li>
        <li> Created a Lambda function (LF1) as a code hook for Lex, which essentially entails the invocation of the Lambda before Lex responds to any of your requests. This helps to manipulate and validate parameters as well as format the bot’s responses.</li>
        <li> The bot use three intents:</li>
         <ul> 
            <li> GreetingIntent : response such as <b>“Hi there, how can I help?” </b> </li>
            <li> ThankYouIntent : <b>"Thank you" </b> </li>
            <li> DiningSuggestionsIntent</li>
        </ul>
        <li> For the DiningSuggestionsIntent, the chat bot collect at least one of the following pieces of information from the user, through conversation: </li>
        <ul>
            <li> Location </li>
            <li> Cuisine </li>
            <li> Dining Time </li>
            <li> Number of people </li>
            <li> Phone number </li>
        </ul>
      </ul>
  <li> Based on the parameters collected from the user, the information is then pushed to an SQS queue (Q1). </li>
  <li> Send a confirmation to the user that the user will receive the suggestions over SMS. </li>
  <li> Integrated the Lex chatbot into your chat API </li>
    <ul>
        <li> Used the AWS SDK to call your Lex chatbot from the API Lambda (LF0). </li>
        <li> API receives a request: </li>
        <ul>
          <li> extract the text message from the API request, </li>
          <li> send it to your Lex chatbot, </li>
          <li> wait for the response, </li>
          <li> response back from Lex as the API response. </li>
        </ul>
    </ul>  
  <li> Used the Yelp API to collect 5,000+ random restaurants from Manhattan. </li>
  <li> DynamoDB (a noSQL database) </li>
    <ul>
        <li> Create a DynamoDB table and named “yelp-restaurants” </li>
        <li> Store the restaurants you scrape, in DynamoDB because some restaurants might have more or less fields than others, which makes DynamoDB ideal for storing this data </li>
        <li> Only Stored the information that are necessary for your recommendation like Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code </li>
    </ul>
  <li> Created an ElasticSearch instance using the AWS ElasticSearch Service. </li>
    <ul>
        <li> Created an ElasticSearch index called “restaurants”  </li>
        <li> Create an ElasticSearch type under the index “restaurants” called “Restaurant”  </li>
        <li> Stored the RestaurantID and Cuisine for each restaurant scraped in ElasticSearch under the “restaurants” index, where each entry has a “Restaurant” data type. </li>
    </ul>
  <li> Build a suggestions module, that is decoupled from the Lex chatbot. </li>
    <ul>
        <li> Create a new Lambda function (LF2) that acts as a queue worker. </li>
        <li> Whenever it is invoked it </li>
          <ol>
              <li> pulls a message from the SQS queue (Q1), </li>
              <li> gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB,  </li>
              <li> formats them </li>
              <li> sends them over text message to the phone number included in the SQS message, using SNS </li>
         </ol>
   </ul>
  <li> Use the DynamoDB table “yelp-restaurants” (which was created from Step 1) to fetch more information about the restaurants (restaurant name, address, etc.), since the restaurants stored in ElasticSearch will have only a small subset of fields from each restaurant. </li>
  <li> Set up a CloudWatch event trigger that runs every minute and invokes the Lambda function as a result. This automates the queue worker Lambda to poll and process suggestion requests on its own. </li>
</ol>

In summary, based on a conversation with the customer,the LEX chatbot will identify the customer’s preferred ‘cuisine and will search using ElasticSearch to receive random suggestions of restaurant IDs with cuisine. At this point, we need to query the DynamoDB table with these restaurant IDs to find more information about the restaurants and suggest to customers like name and address of the restaurant.
