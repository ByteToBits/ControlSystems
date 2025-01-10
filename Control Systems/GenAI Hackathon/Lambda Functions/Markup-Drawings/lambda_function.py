from PIL import Image, ImageDraw, ImageFont
import os
import json
import boto3
import csv  # Import the CSV module
from datetime import datetime, timedelta

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Extract values from the config
bucketName = config["S3"]["bucketName"]
imageBin = config["S3"]["workspace"]["image_bin"]
output = config["S3"]["workspace"]['output']
dynamoTable = config["dynamoDB"]["tableName"]

# Initialize AWS clients
clientS3 = boto3.client('s3')
clientDynamoDB = boto3.client('dynamodb')

# Define fixed values for Project and Equipment
project_name = "Dyson"
equipment_name = "FCU"

# Prepare CSV output path
csv_output_path = "/tmp/output_data.csv"

group_colors = {
    1: "red", 2: "darkgreen", 3: "blue", 4: "darkorange", 5: "purple", 6: "darkred",
    7: "darkblue", 8: "darkcyan", 9: "magenta", 10: "brown", 11: "darkviolet", 12: "navy",
    13: "teal", 14: "darkslategray", 15: "gray", 16: "gold", 17: "coral", 18: "plum", 19: "chocolate", 20: "olive"
}

# Query DynamoDB Function
def queryDynamoDB(table_Name, processID, processType): 
    try: 
        response = clientDynamoDB.get_item(
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

# Update DynamoDB Data
def writeDynamoDB(table_Name, processID, processType, dataReady, timestamp, state, error): 
    try:
        clientDynamoDB.put_item(
            TableName=table_Name, 
            Item={
                'Process': {'S': processID},  
                'Type': {'S': processType}, 
                'Data': {'S': str(dataReady)}, 
                'Last Executed': {'S': str(timestamp)},
                'State': {'S': str(state)},
                'Error': {'S': str(error)},
            }
        )
        print("Successfully written to DynamoDB.")
    except clientDynamoDB.exceptions.ClientError as e: 
        print(f"Failed to write to DynamoDB: {e}")

font = ImageFont.load_default() 

def lambda_handler(event, context): 
    try:
        # Update the Lambda Function Status in DynamoDB
        current_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%S')
        writeDynamoDB(dynamoTable, "MarkUp-Drawing", "ExecutionData", "Not Ready", current_time, "Active", "None")

        # Fetch Images from the S3 Bucket from Image Bin
        schematic_image_key = f"{imageBin}/Schematic.jpg" 
        local_image_path = "/tmp/Schematic.jpg"

        # Download the image
        clientS3.download_file(bucketName, schematic_image_key, local_image_path)

        # Load image
        Image.MAX_IMAGE_PIXELS = None  # Suppress DecompressionBombWarning
        image = Image.open(local_image_path)
        draw = ImageDraw.Draw(image)

        # Query DynamoDB for the Width and Height of Each Tile
        tileSplitterData = queryDynamoDB(dynamoTable, "Tile-Splitter", "Execution Data")
        tileWidth = int(tileSplitterData.get('Tile Width', {}).get('N', 3725))
        tileHeight =  int(tileSplitterData.get('Tile Height', {}).get('N', 3508))

        # Query DynamoDB for Grouping Data Results
        groupingData = queryDynamoDB(dynamoTable, "GroupingData", "ExecutionData")
        groupingDataResults = json.loads(groupingData.get('Results', {}).get('S', '{}')).get("Clusters", [])

        # Parse the Results string from groupingData
        results_string = groupingData.get('Results', {}).get('S', '{}')
        results_data = json.loads(results_string)

        with open(csv_output_path, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write the header
            csv_writer.writerow(['Project', 'Equipment', 'X', 'Y', 'Tile', 'Group', 'GroupX', 'GroupY'])

            # Loop through the clusters to write rows
            for cluster in results_data.get("Clusters", []):
                tile_number = cluster["Centroid"]["Tile"]
                group = cluster["Group"]
                group_x = cluster["Centroid"]["X"]
                group_y = cluster["Centroid"]["Y"]
                # Calculate offsets based on tile number
                if tile_number <= 4:
                    tile_x_offset = (tile_number - 1) * tileWidth
                    tile_y_offset = 0
                elif tile_number <= 8:
                    tile_x_offset = (tile_number - 5) * tileWidth
                    tile_y_offset = tileHeight
                elif tile_number <= 12:
                    tile_x_offset = (tile_number - 9) * tileWidth
                    tile_y_offset = tileHeight * 2

                # Calculate final GroupX and GroupY with offsets
                adjusted_group_x = group_x + tile_x_offset
                adjusted_group_y = group_y + tile_y_offset

                for fcu in cluster["FCU"]:
                    fcu_x = fcu["X"]
                    fcu_y = fcu["Y"]
                    adjusted_fcu_x = fcu_x + tile_x_offset
                    adjusted_fcu_y = fcu_y + tile_y_offset

                    # Write the row with the extracted data
                    csv_writer.writerow([project_name, equipment_name, adjusted_fcu_x, adjusted_fcu_y, tile_number, group, adjusted_group_x, adjusted_group_y])

        # Upload the CSV to S3
        csv_output_key = f"Workspace/Equipment List/EquipmentList.csv"  
        clientS3.upload_file(csv_output_path, bucketName, csv_output_key)
        print("CSV file created and uploaded to S3.")

        # Draw bounding boxes and centroids
        for cluster in groupingDataResults:
            tile_number = cluster["Centroid"]["Tile"]
            
            if tile_number <= 4: 
                tile_x_offset = (tile_number - 1) * tileWidth  
                tile_y_offset = 0
            elif tile_number <= 8: 
                tile_x_offset = (tile_number - 5) * tileWidth  
                tile_y_offset = tileHeight
            elif tile_number <= 12: 
                tile_x_offset = (tile_number - 9) * tileWidth  
                tile_y_offset = tileHeight * 2

            # Draw centroid
            centroid_x = cluster["Centroid"]["X"] + tile_x_offset
            centroid_y = cluster["Centroid"]["Y"] + tile_y_offset
            # Draw "X"
            x_size = 50  # Size of the "X"
            draw.line((centroid_x - x_size, centroid_y - x_size, centroid_x + x_size, centroid_y + x_size), fill="black", width=20)
            draw.line((centroid_x - x_size, centroid_y + x_size, centroid_x + x_size, centroid_y - x_size), fill="black", width=20)

            # Label the group
            label = f"Group {cluster['Group']}"
            draw.text((centroid_x + x_size + 5, centroid_y - 5), label, fill="black", font=font)

            for fcu in cluster["FCU"]:
                global_x = fcu["X"] + tile_x_offset
                global_y = fcu["Y"] + tile_y_offset
                width = fcu["Width"]
                height = fcu["Height"]

                # Draw FCU bounding box
                draw.rectangle(
                    [global_x, global_y, global_x + width, global_y + height],
                    outline=group_colors.get(cluster["Group"], "black"),
                    width=15
                )
        
        # Store the Image inside the output bucket of S3
        output_image_path = "/tmp/MarkUp_Schematic.jpg"
        image.save(output_image_path)

        # Upload the processed image back to S3
        output_image_key = f"{output}/MarkUp_Schematic.jpg"
        clientS3.upload_file(output_image_path, bucketName, output_image_key)

        # Create and save a compressed version of the image
        compressed_image_path = "/tmp/Compressed_Schematic.jpg"
        compressed_image = image.resize((image.width // 3, image.height // 3), Image.LANCZOS)
        compressed_image.save(compressed_image_path, "JPEG", quality=85)

        # Upload the compressed image back to S3
        compressed_image_key = f"{output}/Compressed_Schematic.jpg"
        clientS3.upload_file(compressed_image_path, bucketName, compressed_image_key)

        # Update the Lambda Function Status in DynamoDB
        writeDynamoDB(dynamoTable, "MarkUp-Drawing", "ExecutionData", "Ready", current_time, "Inactive", "None")

        print("Image processing completed and uploaded to S3.")
        
        # Return statement
        return {
            'statusCode': 200,
            'body': json.dumps({
                'output': output_image_key,
                'compressed_output': compressed_image_key
            })
        }

    except Exception as e:  
        print(f"Error in Lambda function: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
