import base64
import json
import http.client
import ssl
import boto3
import os

def get_aws_secrets(secret_name) -> dict:
    region = 'YOUR_AWS_REGION' #Your AWS Region
    my_session = boto3.session.Session(region_name=region)
    client = my_session.client(
        service_name='secretsmanager',
        region_name=region,
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    secret_str = json.loads(get_secret_value_response['SecretString'])
    return secret_str

class AyxAppExecutor:
    def __init__(self):
        #Retrieve values from AWS secrets
        secret_name = os.getenv('SECRETS_NAME', None) #Your AWS Secret Manager's secret name
        secret_str = get_aws_secrets(secret_name)
        print(secret_str)

        api_key = secret_str.get('API_KEY', None) #Your Alteryx Server API Key - which supposed to saved in your AWS Secrets Manager as 'API_KEY'
        api_secret = secret_str.get('API_SECRET', None) #Your Alteryx Server API Secret - which supposed to saved in your AWS Secrets Manager as 'API_Secret'
        pem_string = secret_str.get('PEM_STRING', None) #Your Alteryx Server Certificate in string format- which supposed to saved in your AWS Secrets Manager as 'PEM_STRING'
        ca_string = "-----BEGIN CERTIFICATE-----\n" + pem_string + "\n" + "-----END CERTIFICATE-----"
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.ca_string = ca_string
        self.token = self.get_access_token()
        self.ayx_url = "YOUR_ALTERYX_URL/DOMAIN_NAME" #e.g. gallery.xxx.com

    def get_access_token(self): #Get authorisation token for your Alteryx gallery
        auth_url = f"https://{self.ayx_url}/webapi/oauth2/token"
        auth_header = f"{self.api_key}:{self.api_secret}"
        base64_bytes = base64.b64encode(auth_header.encode()).decode()
        connection = self.connection()
        
        try:
            connection.request(
                "POST", 
                auth_url, 
                body="grant_type=client_credentials", 
                headers={"Authorization": f"Basic {base64_bytes}"}
            )
            response = connection.getresponse()
            print(f'status code: {response.status}') #Debugging purpose
            response_data = response.read().decode("utf-8")
            connection.close()
            token = json.loads(response_data)["access_token"]
            print("Authorization successful. Returning Access Token")
            return token
        except Exception as ex:
            print(f"Authorization failed. {ex}")
            return None
        
    def connection(self): #Set up SSL connection
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_verify_locations(cadata=self.ca_string)
        ssl_connection = http.client.HTTPSConnection(
            self.ayx_url,
            context=ssl_context
        )
        return ssl_connection

    def execute_app(self, app_id, json_payload): #Run the workflow based on app_id
        job_url = f"https://{self.ayx_url}/webapi/user/v2/workflows/{app_id}/jobs/" #Modify to use other APIs if needed
        headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-type": "application/json"
            }
        connection = self.connection()

        try:
            connection.request(
                "POST", 
                job_url, 
                body=json_payload, 
                headers=headers
            )
            response = connection.getresponse()
            print(f'status code: {response.status}')
            response_data = response.read().decode("utf-8")
            connection.close()
            print(f"Successfully executed app: {app_id} - status code: {response.status}")
            return response_data
        except Exception as ex:
            print("Failed to execute: ", ex)
            return None