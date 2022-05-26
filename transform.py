# Original code from post below, rights to the original owner, do not claim to have made this.
#https://stackoverflow.com/questions/58396131/how-to-identify-largest-bounding-rectangles-from-an-image-and-separate-them-into

# use two percentages to create a cell
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
# use two percentages to create a cell

def round_down_to_next_multiple_of_8(a):
    return a & (-8)

def rotate_image(image, angle):
    # Grab the dimensions of the image and then determine the center
    #print()
    (h, w) = image.shape[:2]
    #print(f"Height: {h}, Width: {w}")
    (cX, cY) = (w / 2, h / 2)
    #print(f"cX: {cX}, cY: {cY}")

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    #print(f"getRotationMatrix2D: {M}")
    cos = np.abs(M[0, 0]) # Calculates absolute value elementwise in array
    #print(f"cos: {cos}")
    sin = np.abs(M[0, 1])
    #print(f"sin: {sin}")

    # Compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    #print(f"new width: {nW}")

    nH = int((h * cos) + (w * sin))
    #print(f"new height: {nH}")

    # Adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    #print(f"Adjusted Rotation [0, 2]: {M}")

    M[1, 2] += (nH / 2) - cY
    #print(f"Adjusted Rotation [1, 2]: {M}")
    #print()
    # Perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def perspective_transform(image, corners):
    def order_corner_points(corners):
        # Separate corners into individual points
        # Index 0 - top-right
        #       1 - top-left
        #       2 - bottom-left
        #       3 - bottom-right
        corners = [(corner[0][0], corner[0][1]) for corner in corners]
        top_r, top_l, bottom_l, bottom_r = corners[0], corners[1], corners[2], corners[3]
        print()
        print(f"top_r: {top_r} top_l: {top_l} bottom_l: {bottom_l} bottom_r: {bottom_r}")
        return (top_l, top_r, bottom_r, bottom_l)

    # Order points in clockwise order
    ordered_corners = order_corner_points(corners)
    top_l, top_r, bottom_r, bottom_l = ordered_corners

    # Determine width of new image which is the max distance between 
    # (bottom right and bottom left) or (top right and top left) x-coordinates
    width_A = np.sqrt(((bottom_r[0] - bottom_l[0]) ** 2) + ((bottom_r[1] - bottom_l[1]) ** 2))
    print(f"width_A: {width_A}")
    width_B = np.sqrt(((top_r[0] - top_l[0]) ** 2) + ((top_r[1] - top_l[1]) ** 2))
    print(f"width_B: {width_A}")
    width = max(int(width_A), int(width_B))

    # Determine height of new image which is the max distance between 
    # (top right and bottom right) or (top left and bottom left) y-coordinates
    height_A = np.sqrt(((top_r[0] - bottom_r[0]) ** 2) + ((top_r[1] - bottom_r[1]) ** 2))
    print(f"height_A: {height_A}")
    height_B = np.sqrt(((top_l[0] - bottom_l[0]) ** 2) + ((top_l[1] - bottom_l[1]) ** 2))
    print(f"height_B: {height_B}")
    height = max(int(height_A), int(height_B))

    # Construct new points to obtain top-down view of image in 
    # top_r, top_l, bottom_l, bottom_r order
    dimensions = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], 
                    [0, height - 1]], dtype = "float32")
    print(f"Dimensions: {dimensions}")

    # Convert to Numpy format
    ordered_corners = np.array(ordered_corners, dtype="float32")
    print(f"ordered_corners numpy: {ordered_corners}")

    # Find perspective transform matrix
    matrix = cv2.getPerspectiveTransform(ordered_corners, dimensions)
    print(f"getPerspectiveTransform: {matrix}")

    # Return the transformed image
    print()
    return cv2.warpPerspective(image, matrix, (width, height))

cap = cv2.VideoCapture("Video\\test1639658932.91_Trim.mp4")

while(cap.isOpened()):
    ret, frame = cap.read() # Returns next video frame
    original = frame.copy() # Copies frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Makes image gray.
    # Transforms the gray image into a binary image.
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,3)
    

    cv2.imshow('thresh', thresh) # Shows the adaptaiveThreshold

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Helps with object detection.
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:3]

    ROI_number = 0 # Region Of Interest
    for c in cnts:
        peri = cv2.arcLength(c, True) # Calcualtes contour perimeter.
        approx = cv2.approxPolyDP(c, 0.015 * peri, True) # Approximates polygonal curves, keeping precsion. 

        if len(approx) == 4: # 4 Corners
            cv2.drawContours(frame,[c], 0, (36,255,12), 3) # Draws contour lines in image.
            transformed = perspective_transform(original, approx) # Passes the polygonal curves and the image frame to function.
            rotated = rotate_image(transformed, -90) # Passes the transformed to the rotate function. 
            cv2.imwrite('ROI_{}.png'.format(ROI_number), rotated) # Saves the image
            cv2.imshow('ROI_{}'.format(ROI_number), rotated) # Shows the image.
            ROI_number += 1
 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
cv2.waitKey()