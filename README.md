# Triggering_Alteryx_API_via_AWS_Lambda

This is a project demonstrating an AWS Lambda that runs an Alteryx workflow from the Alteryx server/gallery via Alteryx gallery v2 APIs. As a result, you would be able to trigger your Alteryx workflow using AWS Events (such as s3, cloud watch events, SQS etc. The scripts were written in python 3.11.

## Requirements
1. AWS user
2. Python Libraries such as SSL, boto3 etc.
3. Alteryx Server User with Artisan and API Access.
4. (optional) CI/CD pipeline to upload your lambda into your AWS server - not demonstrated in this project.
