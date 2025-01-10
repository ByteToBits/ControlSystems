import json
import boto3
import io
from PIL import Image
from datetime import datetime, timedelta
import pyUtilities

# Initialize AWS clients
rekognition = boto3.client('rekognition')
awsS3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
lambdaClient = boto3.client('lambda')

def loadImageS3(bucket_name, image_key):
    try:
        s3_object = awsS3.get_object(Bucket=bucket_name, Key=image_key)
        image_stream = io.BytesIO(s3_object['Body'].read())
        return Image.open(image_stream)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def detectFCULabels(image, rekognition, project_version_arn, max_results, min_confidence):
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        response = rekognition.detect_custom_labels(
            ProjectVersionArn=project_version_arn,
            Image={'Bytes': buffer.getvalue()},
            MaxResults=max_results,
            MinConfidence=min_confidence
        )
        return response
    except Exception as e:
        print(f"Error calling Rekognition: {e}")
        return None

def queryDynamoDB(dynamo_table, processID, processType):
    try:
        response = dynamodb.get_item(
            TableName=dynamo_table,
            Key={
                'Process': {'S': f'{processID}'},
                'Type': {'S': f'{processType}'}
            }
        )
        return response['Item'] if 'Item' in response else None
    except Exception as e:
        print(f"Error fetching {processID} data: {e}")
        return None

def updateDynamoDB(dynamo_table, process, type_value, current_time, fcu_data=None, data_status="", state="", error=""):
    try:
        # Compute total FCUs if data is provided
        total_fcus = sum(int(fcu["Number of FCU"]) for fcu in fcu_data.values()) if fcu_data else 0
        update_expression = "SET #last_executed = :last_executed"
        expression_attribute_values = {
            ':last_executed': {'S': current_time}
        }
        
        if data_status:
            update_expression += ", #data = :data"
            expression_attribute_values[':data'] = {'S': data_status}
        
        if state:  # Include state in the update
            update_expression += ", #state = :state"
            expression_attribute_values[':state'] = {'S': state}
        
        if error:  # Include error in the update
            update_expression += ", #error = :error"
            expression_attribute_values[':error'] = {'S': error}
        
        if fcu_data is not None:
            update_expression += ", #number_of_fcu = :number_of_fcu, #results = :results"
            expression_attribute_values.update({
                ':number_of_fcu': {'N': str(total_fcus)},
                ':results': {'S': json.dumps(fcu_data)}  # Store as a JSON string
            })
        
        dynamodb.update_item(
            TableName=dynamo_table,
            Key={
                'Process': {'S': process},
                'Type': {'S': type_value}
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames={
                '#last_executed': 'Last Executed',
                '#number_of_fcu': 'Number of FCU',
                '#results': 'Results',
                '#data': 'Data',
                '#state': 'State',
                '#error': 'Error'
            },
            ExpressionAttributeValues=expression_attribute_values
        )
    except Exception as e:
        print(f"Error updating DynamoDB: {e}")
        print(f"fcu_data received: {fcu_data}")

def lambda_handler(event, context):
    # Load configuration from config.json
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Extract configuration variables
    bucket_name = config['S3']['bucketName']
    image_tiles = config['S3']['workspace']['image_tiles']
    project_version_arn = config['rekognition']['projectARN']
    dynamo_table = config['dynamoDB']['tableName']

    # Get Overlap Filter Settings 
    overlapFilterEnable = config['rekognition']['overlapFilter']
    iou_threshold = config['rekognition']['overlapThreshold']

    # Fetch Tile Splitter Data (Width and Height in Pixels)
    tileSplitterData = queryDynamoDB(dynamo_table, "Tile-Splitter", "Execution Data")
    tile_height = int(tileSplitterData['Tile Height']['N'])
    tile_width = int(tileSplitterData['Tile Width']['N'])
    
    # Fetch the Max Results and Model Confidence 
    rekognitionParameters = queryDynamoDB(dynamo_table, "Rekognition-Broker", "ExecutionData")
    rekognition_MaxResults = int(rekognitionParameters['Max Results']['N'])
    rekognition_MinConfidence = float(rekognitionParameters['Min Confidence']['N'])

    # Initialize result storage
    all_detected_fcus = {
        f"Tile: {i}": {
            "Number of FCU": 0,
            "Response": []
        } for i in range(1, 2)
    }

    current_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%S')
    # Initialize the Table
    updateDynamoDB(dynamo_table, "Rekognition-Broker", "ExecutionData", current_time, fcu_data="", data_status="Not Ready", state="Active", error = "None")
    # Iterate through all 12 Tile Images
    for i in range(1, 13):  
        image_file = f"{image_tiles}/Schematic_Tile_{i}.jpg"
        image = loadImageS3(bucket_name, image_file)

        if image is None:
            error = f'Failed to load image {image_file} from S3'
            updateDynamoDB(dynamo_table, "Rekognition-Broker", "ExecutionData", current_time, fcu_data="", data_status="Not Ready", state="Inactive", error = error)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': error})
            }

        # Call Rekognition Custom Labels API to detect FCU objects
        response = detectFCULabels(image, rekognition, project_version_arn, rekognition_MaxResults, rekognition_MinConfidence)

        # Extract detected FCUs and filter based on IOU
        detected_fcus = []
        for label in response['CustomLabels']:
            confidence = round(float(label['Confidence']), 2)
            bounding_box = label['Geometry']['BoundingBox']
            detected_fcus.append({
                'Confidence': confidence,
                'X': round(bounding_box['Left'] * tile_width),
                'Y': round(bounding_box['Top'] * tile_height),
                'Width': round(bounding_box['Width'] * tile_width),
                'Height': round(bounding_box['Height'] * tile_height)
            })

        # Apply IOU filtering to detected FCUs
        filtered_fcus = pyUtilities.filterBoundingBoxes(detected_fcus, iou_threshold, overlapFilterEnable)

        # Update the FCU data for the current tile
        all_detected_fcus[f"Tile: {i}"] = {
            "Number of FCU": len(filtered_fcus),
            "Response": filtered_fcus
        }

    # Set Data to Ready after completion
    updateDynamoDB(dynamo_table, "Rekognition-Broker", "ExecutionData", current_time, fcu_data=all_detected_fcus, data_status="Ready", state="Inactive", error = "None")
    
    lambdaClient.invoke(
        FunctionName = "",
        InvocationType='Event',  
    )

    return {
        'statusCode': 200,
        'body': json.dumps(all_detected_fcus, indent=4)
    }
