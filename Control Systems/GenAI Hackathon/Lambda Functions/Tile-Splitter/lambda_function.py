import os
import json
import subprocess
import boto3
from PIL import Image
from datetime import datetime, timedelta

activeProject = 'Dyson'

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Extract values from the config
bucket_name = config["S3"]["bucketName"]
schematic_folder = config["S3"]["workspace"]["schematic"]
image_bin = config["S3"]["workspace"]["image_bin"]
image_tiles = config["S3"]["workspace"]["image_tiles"]
dynamo_table = config["dynamoDB"]["tableName"]

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
lambdaClient = boto3.client('lambda')
dpi = 450  

def resetDB_Data():
    target_processes = ["Rekognition-Broker", "GroupingData", "MarkUp-Drawing"]
    type_value = "ExecutionData"

    for process in target_processes:
        dynamodb.update_item(
            TableName=dynamo_table,
            Key={
                'Process': {'S': process},
                'Type': {'S': type_value}
            },
            UpdateExpression="SET #data = :data",
            ExpressionAttributeNames={
                '#data': 'Data'
            },
            ExpressionAttributeValues={
                ':data': {'S': 'Not Ready'}
            }
        )

def update_dynamo_item(process, type_value, state, data="", error="", height=0, width=0):
    
    # Get current UTC time
    utc_time = datetime.utcnow()
    dubai_time = utc_time + timedelta(hours=8)
    current_time = dubai_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5]  
    
    # Check if the item already exists
    response = dynamodb.get_item(
        TableName=dynamo_table,
        Key={
            'Process': {'S': process},
            'Type': {'S': type_value}
        }
    )

    if 'Item' in response:
        # Item exists, proceed with update
        dynamodb.update_item(
            TableName=dynamo_table,
            Key={
                'Process': {'S': process},
                'Type': {'S': type_value}
            },
            UpdateExpression="SET #state = :state, #data = :data, #error = :error, #last_executed = :last_executed, #height = :height, #width = :width",
            ExpressionAttributeNames={
                '#state': 'State',
                '#data': 'Data',
                '#error': 'Error',
                '#last_executed': 'Last Executed',
                '#height': 'Tile Height',
                '#width': 'Tile Width'
            },
            ExpressionAttributeValues={
                ':state': {'S': state},
                ':data': {'S': data}, 
                ':error': {'S': error},
                ':last_executed': {'S': current_time},
                ':height': {'N': str(height)},
                ':width': {'N': str(width)}
            }
        )
    else:
        print("Error: Attempted to update an immutable item that does not exist.")

def lambda_handler(event, context):
    
    # Set all the Data to "Not Ready Status"
    resetDB_Data() 
    quadrant_width = 0 
    quadrant_height = 0

    try: 

        # Update DynamoDB to indicate the process is starting
        update_dynamo_item("Tile-Splitter", "Execution Data", "Active", "Not Ready", height=0, width=0)

        # List PDF files in the specified S3 schematic directory
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=schematic_folder)

        pdf_file_key = None
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.pdf'):
                pdf_file_key = obj['Key']
                break

        if not pdf_file_key:
            update_dynamo_item("Tile-Splitter", "Execution Data", "Inactive", error="No PDF files found")
            return {
                'statusCode': 404,
                'body': 'No PDF files found in the specified directory.'
            }

        # Download the PDF file from S3
        s3.download_file(bucket_name, pdf_file_key, '/tmp/Schematic.pdf')

        # Path to pdftocairo in the Poppler layer
        pdftocairo_path = '/opt/poppler/bin/pdftocairo'
        
        # Set the LD_LIBRARY_PATH to include the poppler/lib directory
        os.environ['LD_LIBRARY_PATH'] = '/opt/poppler/lib'

        # Convert PDF to JPEG using pdftocairo with specified DPI
        command = [pdftocairo_path, '-jpeg', '-r', str(dpi), '/tmp/Schematic.pdf', '/tmp/output']

        try:
            # Capture stdout and stderr
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("pdftocairo output:", result.stdout)
            print("pdftocairo errors:", result.stderr)
        except subprocess.CalledProcessError as e:
            print("Error running pdftocairo:", e)
            update_dynamo_item("Tile-Splitter", "Execution Data", "Inactive", error=str(e))
            raise e

        # List files in /tmp to check the output
        output_files = [f for f in os.listdir('/tmp') if f.startswith('output')]
        print("Generated output files:", output_files)

        # Check if the expected file was created
        if not output_files:
            update_dynamo_item("Tile-Splitter", "Execution Data", "Inactive", "Not Ready", error="No output files generated")
            return {
                'statusCode': 500,
                'body': 'No output files were generated.'
            }

        # Check if any generated file is valid
        valid_file = None
        for file in output_files:
            full_path = os.path.join('/tmp', file)
            if os.path.getsize(full_path) > 0:  # Check for non-empty files
                valid_file = full_path
                break

        if not valid_file:
            update_dynamo_item("Tile-Splitter", "Execution Data", "Inactive", "Not Ready", error="Generated image is empty")
            return {
                'statusCode': 500,
                'body': 'Generated image is empty.'
            }

        # Upload the resulting JPEG file back to S3 with a fixed name
        s3.upload_file(valid_file, bucket_name, image_bin + "/Schematic.jpg")

        # Split the image into tiles
        image = Image.open(valid_file)
        width, height = image.size

        # Calculate the initial quadrant dimensions
        quadrant_width = width // 4
        quadrant_height = height // 3

        # Initialize height and width for the update
        tile_height, tile_width = 0, 0

        # Upload quadrants 
        for row in range(3):
            for col in range(4):
                left = col * quadrant_width
                upper = row * quadrant_height
                right = left + quadrant_width
                lower = upper + quadrant_height

                quadrant = image.crop((left, upper, right, lower))

                # Check dimensions and resize if necessary
                if quadrant.width > 4000 or quadrant.height > 4000:
                    # Calculate the scaling factor
                    scaling_factor = min(4000 / quadrant.width, 4000 / quadrant.height)
                    new_size = (int(quadrant.width * scaling_factor), int(quadrant.height * scaling_factor))
                    quadrant = quadrant.resize(new_size, Image.ANTIALIAS)

                quadrant_name = f"Schematic_Tile_{row * 4 + col + 1}.jpg"
                quadrant_path = os.path.join('/tmp', quadrant_name)

                quadrant.save(quadrant_path)
                s3.upload_file(quadrant_path, bucket_name, image_tiles + f"/{quadrant_name}")

                # Update the tile height and width
                tile_height = max(tile_height, quadrant.height)
                tile_width = max(tile_width, quadrant.width)

        # # JSON Payload
        # claudePayload = {
        #     "tileWidth": f"{quadrant_width}", 
        #     "tileHeight": f"{quadrant_height}",
        #     "activeProject": f"{activeProject}"
        # }
        
        # # Change Here: Test Invoke Claude
        lambdaClient.invoke(
           FunctionName = "",
           InvocationType='Event',  
        )

        # Update the DynamoDB 
        update_dynamo_item("Tile-Splitter", "Execution Data", "Inactive", "Ready", error="None", height=tile_height, width=tile_width)

        return {
            'statusCode': 200,
            'body': f'PDF converted & uploaded to S3 | Claude Invoked'
        }

    finally:
        # List all objects inside the schematic folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=schematic_folder)
        if 'Contents' in response:
            # Filter to delete only PDF files
            delete_keys = [{'Key': obj['Key']} for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
            if delete_keys:
                s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_keys})
                print(f"Deleted {len(delete_keys)} PDF files from {bucket_name}/{schematic_folder}")