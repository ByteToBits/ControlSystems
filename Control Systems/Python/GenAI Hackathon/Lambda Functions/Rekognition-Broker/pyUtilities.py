
# https://github.com/PyImageSearch/imutils/blob/master/imutils/object_detection.py
# Adapted version of non_max_suppression

#  non_max_suppression for calculating overlap Threshold or Intersection over Union

def calculateOverlap(boxA, boxB):

    # Calculate the coordinates of the intersection rectangle
    # Fetch the Max Coordinates of the Boxes (Top Left Vertex) - Since by Default Recognition gives the Coordinates for these (Not Centroid)
    xA = max(boxA['X'], boxB['X'])
    yA = max(boxA['Y'], boxB['Y'])
    
    # Fetch the Minimum of the Boxes (Bottom Right Vertex)
    xB = min(boxA['X'] + boxA['Width'], boxB['X'] + boxB['Width'])
    yB = min(boxA['Y'] + boxA['Height'], boxB['Y'] + boxB['Height'])

    # Calculate Intersection - Value Should be in Positve | Clamp to 0 for no intersection
    interWidth = max(0, xB - xA)
    interHeight = max(0, yB - yA)
    interArea = interWidth * interHeight

    # Calculate the area of both bounding boxes
    boxAArea = boxA['Width'] * boxA['Height']
    boxBArea = boxB['Width'] * boxB['Height']

    # Return Intersection Over Union in Percentage 0 = 0% and 0.5 = 50% 
    overlapPercentage = interArea / float(boxAArea + boxBArea - interArea)
    return overlapPercentage

# Filter Bounding Boxes Based on IOU
def filterBoundingBoxes(detected_boxes, iou_threshold, enableIOU):

    # Break if the disabled
    if not enableIOU:
        return detected_boxes
    
    # Initialize Empty Array
    filteredBoxes = []
    
    # Iterate through all the Bounding Boxes in the Array
    for box in detected_boxes:
        keepBox = True
        # Iterate through the alreay filtered array of boxes to find Intersect
        for otherBox in filteredBoxes:
            overlapPercentage = calculateOverlap(box, otherBox)
            if overlapPercentage > iou_threshold:
                keepBox = False
                break
        if keepBox: # Only keep boxes within the permissible threshold
            filteredBoxes.append(box)
    return filteredBoxes