#!/usr/bin/env python3
"""
Occupancy Detection Function File used to Determine the Number of Occupants 
in a given image or video stream and returns the value as a Integer
"""
__author__ = "Tristan Sim"
__version__ = "1.0.1"
__status__ = "Prototype"

import cv2
import os
from ultralytics import YOLO
from datetime import datetime

# Initialize: Load Computer Vision Model
print("Loading YOLO Model...")
try: 
   model = YOLO('yolov8n.pt')
   print("Successfully Loaded YOLO Model...")
except:
    print("Error Loading YOLO Model...")

# Function: Stream the Webcam Footage using OpenCV
def start_video_stream():
    """
    Start Live Video Stream with Real-time Occupant Detection
    Returns:
        currentOccupantCount: The Number of Occupants in the Final Frame when Function Ends
    """
    
    print("Starting Video Stream...")
    print("Press 'q' to exit stream")
    
    # Initialize Variables
    videoStream = cv2.VideoCapture(0)
    currentOccupantCount = 0
    
    if not videoStream.isOpened():
        print("Error: Could Not Launch Video Stream!")
        return currentOccupantCount

    # Define the Video Capture Properties
    videoStream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    videoStream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    while True:

        # Read Frame from the Video Stream
        # status (Boolean): Indicates if Frame is Successfully Captureed
        # frameData (Numpy Array): Image/Video Frame Data (Contains Height, Width, Colour Channels)
        status, frameData = videoStream.read()
        if not status:
            print("Error:Failed to read data from video stream!")
            break
        
        # Process the Frame Data using YOLO
        occupantCount, annotatedFrame = count_occupants(frameData)
        
        # Update the Occupancy Counts when the Change
        if occupantCount != currentOccupantCount:
            currentOccupantCount = occupantCount
            print(f"Current Occupancy Count is {occupantCount}")
        
        # Stream the Live Video using the Annotated Video Frames
        cv2.imshow("Occupancy Detection Video Stream", annotatedFrame)
        
        # Handle User Input (Wait for Key Press for 1 Millisecond and use Bitwise Operation to keep the Last 8 Bits)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): # ASCII 113
            print("Stopping Video Stream...")
            break
    
    # Release all Resources being Used by the Function
    videoStream.release() 
    cv2.destroyAllWindows()
    
    return currentOccupantCount

# Function: Occupany Detection and Counting
def count_occupants(frame):
    """
    Count the Number of Occupants in a Single Frame Image
    Args:
        frame: OpenCV image/frame
    Returns:
        tuple: (occupant_count, annotated_frame)
    """
    # Run the YOLO detection model
    modelResults = model(frame, verbose=False) # Returns (boxes, segmentation mask, pose keypoints and probabilties)

    annotatedFrame = frame.copy() # Make a copy for annotation
    occupantCount = 0 # Count number of object class (occupants) and draw bounding boxes
    
    for result in modelResults:
        if result.boxes is not None:
            for box in result.boxes:
                classID = int(box.cls[0]) # Object Type Detected (0 = Personm, 1 = Bycicle, 2 = Car and etc)
                confidence = float(box.conf[0])*100       
                # If an Occupant is Detected with Sufficient Confidence
                if classID == 0 and confidence > 50:
                    occupantCount += 1 
                    x1, y1, x2, y2 = map(int, box.xyxy[0]) # Get the Coordinates of Bounding Boxes
                    cv2.rectangle(annotatedFrame, (x1, y1), (x2, y2), (0, 255, 0), 2) # Draw Bounding Boxes
                    label = f"Occupant {occupantCount}: {confidence:.2f} %" 
                    cv2.putText(annotatedFrame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Totalize the Number of Occupants Count
    cv2.putText(annotatedFrame, f"Total Occupants: {occupantCount}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Display timestamp in the image Frame
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(annotatedFrame, timestamp, (10, annotatedFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return occupantCount, annotatedFrame

# Function: Single Shot Image Detection for Single Image Inputs
def single_shot_image_detection(imagePath):
    """ 
    Single-Shot Image Detection Function to Determine Number of Occupants
    in a Single Image and returns the number as an Integer. 
    Args:
       imagePath: String containing the path of the Image
    Returns: 
       occupantCount: The Total Numbner of Occupants in the Image
    """

    # Check if the image file exists
    # Try the provided path first
    if imagePath and os.path.exists(imagePath):     
        pass # Use the provided path
    else: # Default to sample image
       if imagePath:  # If they provided something invalid
           print(f"Invalid path '{imagePath}', using default sample image...")
           imagePath = r"Control Systems\Python\Computer Vision Climate Controls\Resources\Images\SampleImage.jpeg"
    
    try:
        print(f"Loading image: {imagePath}")
        frame = cv2.imread(imagePath) # Load the image using OpenCV
        
        if frame is None:
            print("Error: Could not load image. Please check the file format.")
            return 0
        
        print("Processing image for occupant detection...")
        occupantCount, annotatedFrame = count_occupants(frame)
        
        print(f"Detection Complete! Found {occupantCount} occupant(s)")
        
        # Display the annotated image
        cv2.imshow("Single Shot Occupancy Detection", annotatedFrame)
        print("Press any key to close the image window...")
        cv2.waitKey(0)  # Wait indefinitely for a key press
        cv2.destroyAllWindows()
        
        return occupantCount
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return 0


if __name__ == "__main__":
    
    print("\nOccupancy Detection Test")
    print("\nAvailable Options:")
    print("1. Process Single Image")
    print("2. Start Video Stream")
    print("3. Exit")
    
    while True: 
       userInput = input("Please enter one of the Options Above (Numeric Values from 1-3): ").strip()
       if userInput in ['1', '2', '3']: 
           break
       else: 
           print("Please Etner a Valid Option Listed Above...")

    match userInput: 

        case '1': 
            print("Selected Process Single Image...")
            imagePath = input("Please Enter image path: ").strip()
            result = single_shot_image_detection(imagePath)

        case '2': 
            finalCount = start_video_stream()
            print(f"Final occupancy count: {finalCount}")

        case _:
            print("Invalid choice... Streaming Live Video...")
            finalCount = start_video_stream()
            print(f"Final occupancy count: {finalCount}")