# Telemed API

This application is based on [serverless framework](https://www.serverless.com/framework/docs/providers/aws/).
It is a free and open-source web framework written using Node.js. Serverless is the first framework developed for building applications on AWS Lambda.

AWS Lambda is an event-driven, serverless computing platform provided by Amazon as a part of Amazon Web Services. It is a computing service that runs code in response to events and automatically manages the computing resources required by that code.


### List of options that can be performed:

- build: npm install & pip install -r requirements.txt.
- deploy:  serverless deploy --stage STAGENAME --region REGIONNAME -v
- clean: rm -rf DIR/node_modules & rm -rf API_DIR/api/.serverless
- remove: serverless remove --stage STAGENAME --region REGIONNAME -v

### RESTful APIs
- #### documents
    This service helps users to store/retrieve their profile images in S3.
- #### users
    This service is used to manage the users (doctor, patients) of the application.

### Layers Service
It contains all the common dependencies for the lambda functions.

### References
- [Serverless Framework](https://www.serverless.com/framework/docs/providers/aws/guide/intro/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Build a Python REST API with Serverless, Lambda, and DynamoDB](https://www.serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb)
- [Make](https://en.wikipedia.org/wiki/Makefile)
