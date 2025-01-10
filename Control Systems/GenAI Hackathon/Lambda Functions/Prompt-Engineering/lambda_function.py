import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Initialize AWS clients
clientBedrock = boto3.client("bedrock-runtime")
clientDynamoBD = boto3.client('dynamodb')
lambdaClient = boto3.client('lambda')

# Use Claude Sonnet model ID
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Load configuration data from config.json
with open('config.json') as configFile:
    configData = json.load(configFile)

dynameTable = configData['dynamoDB']['tableName']

# Query DynamoDB Function
def queryDynamoDB(table_Name, processID, processType):
    try:
        response = clientDynamoBD.get_item(
            TableName=table_Name,
            Key={
                'Process': {'S': processID},
                'Type': {'S': processType}
            }
        )
        return response.get('Item') 
    except Exception as e:
        print(f"Error fetching {processID} data: {e}")
        return None

# Query DynamoDB for Rekognition data
rekognitionData = queryDynamoDB(dynameTable, "Rekognition-Broker", "ExecutionData") 
rekognitionResults = rekognitionData.get('Results', {}).get('S', None)
rekognitionNumOfFCU = int(rekognitionData.get('Number of FCU', {}).get('N', 0))

# Query DynamoDB for Grouping Data
grouping_data = queryDynamoDB(dynameTable, "GroupingData", "ExecutionData")
max_NumOfFCU = int(grouping_data.get('Max FCU', {}).get('N', 2))  # Fallback Value 2
min_NumOfFCU = int(grouping_data.get('Min FCU', {}).get('N', 5))  # Fallback Value 6
numOfGroup = int(grouping_data.get('Number of Groups', {}).get('N', 15))  # Fallback Value 13

# Write Data to DynamoDB
def writeToDB(response_text, timestamp, executionState, dataReady):
    try:
        clientDynamoBD.put_item(
            TableName=dynameTable,
            Item={
                'Process': {'S': 'GroupingData'},  
                'Type': {'S': 'ExecutionData'}, 
                'Results': {'S': response_text},
                'Max FCU': {'N': str(max_NumOfFCU)},
                'Min FCU': {'N': str(min_NumOfFCU)},
                'Number of Groups': {'N': str(numOfGroup)},
                'Last Executed': {'S': timestamp},
                'Data': {'S': dataReady},
                'State': {'S': executionState}
            }
        )
        print("Successfully written to DynamoDB.")
    except ClientError as e:
        print(f"Failed to write to DynamoDB: {e}")

def lambda_handler(event, context):
    current_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%S')
    writeToDB("", current_time, "Active", "Not Ready")

    if rekognitionResults is None:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Rekognition results not found'})
        }

    input_text = rekognitionResults

    system_prompt = (
        f"Task: System Prompt\n"
        f"Do not respond to this prompt; return only a string. The next prompt will contain raw data for processing.\n"
        f"Your response must be in JSON format; otherwise, the program will encounter runtime errors.\n"
        f"1) Group FCU data into clusters in JSON format.\n"
        f"2) Each cluster represents a control panel for the FCUs, containing {min_NumOfFCU} to {max_NumOfFCU} FCUs.\n"
        f"3) Include a centroid with optimal X and Y coordinates for FCU placement.\n"
        f"4) Strictly format the response as JSON for use in another function.\n"
        f"5) The required number of clusters is user-defined; for this request, it group the {rekognitionNumOfFCU} into {numOfGroup} groups.\n"
        f"6) Provide only the JSON data—no extra text or descriptions.\n"
        f"7) Confidence values may be omitted.\n"
        f"8) If there are overlapping bounding boxes, remove the bigger ones as smaller ones are more accurate"
        f"9) Maintain the Tile origin of each FCU; groups can include FCUs from different Tiles based on optimal location.\n"
        f"10) Tiles represent an image split into 4 columns and 3 rows for easier processing:\n"
        f"   Row 1: [1, 2, 3, 4]\n"
        f"   Row 2: [5, 6, 7, 8]\n"
        f"   Row 3: [9, 10, 11, 12]\n"
        f"10) Avoid generating groups with only 1 FCU; group with adjacent Tiles, adhering to the minimum of {min_NumOfFCU}.\n"
        f"Example Response Format:\n"
        f"{{\n"
        f"  \"Clusters\": [\n"
        f"    {{\n"
        f"      \"Group\": 1,\n"
        f"      \"Centroid\": {{\n"
        f"        \"Tile\": 1,\n"
        f"        \"X\": 3176,\n"
        f"        \"Y\": 2696\n"
        f"      }},\n"
        f"      \"FCU\": [\n"
        f"        {{ \"Tile\": 1, \"X\": 3184, \"Y\": 2704, \"Width\": 129, \"Height\": 117 }},\n"
        f"        {{ \"Tile\": 2, \"X\": 3184, \"Y\": 2704, \"Width\": 129, \"Height\": 117 }}\n"
        f"      ]\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n"
        f"Data is as follows:\n"
    )
    
    # Prepare the request for model invocation
    data_response = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": system_prompt + input_text,
            }
        ],
    }

    request = json.dumps(data_response)

    try:
        # Invoke the model with the request
        response = clientBedrock.invoke_model(modelId=model_id, body=request)

        # Parse the response from the model 
        model_response = json.loads(response["body"].read().decode("utf-8"))
        dataString = model_response['content'][0]['text']
        dataKey = json.loads(dataString)
        writeToDB(json.dumps(dataKey), current_time, "Inactive", "Ready")

        lambdaClient.invoke(
           FunctionName = "",
           InvocationType='Event'  
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'output': dataKey})
        }

    except (ClientError, Exception) as e:  
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
