from repository import AyxAppExecutor
import json

def lambda_handler(event, context):
    print("in lambda handler")
    print(json.dumps(event))
    app_id = "YOUR_ALTERYX_APP_ID"  #Obtained through Alteryx server URL
    json_payload = json.dumps({"questions": [{"name": "", "value": ""}]})
    executor = AyxAppExecutor()
    result = executor.execute_app(app_id, json_payload)
    if result:
        print("Execution result:", result)

if __name__ == "__main__":
    result = lambda_handler(None, None)
    json.dumps(result);
