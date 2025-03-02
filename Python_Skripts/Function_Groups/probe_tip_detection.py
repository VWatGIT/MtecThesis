import cv2
import numpy as np
from .camera import crop_image
from pypylon import pylon

# global variables, TODO implement in UI
mouse_x = -1
mouse_y = -1

def save_new_image(image, filename):
    cv2.imwrite(filename, image)
    print(f"Image saved to {filename}")

def load_image(filename):
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    if image is not None:
        print(f"Image loaded from {filename}")
    else:
        print(f"Failed to load image from {filename}")
    return image
    


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global mouse_x, mouse_y
        mouse_x, mouse_y = x, y
        print(f"Mouse coordinates: ({x}, {y})")
        
def show_image(image):
    cv2.imshow('image', image)
    cv2.setMouseCallback('image', mouse_callback)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def detect_needle_tip(image, threshold=60):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply thresholding
    _, binary_image = cv2.threshold(blurred_image, threshold, 255, cv2.THRESH_BINARY) # TODO adjust threshold value, maybe with slider in GUI

    # Find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_candidates = []
    # Draw contours and find the tip
    for contour in contours:
        if cv2.contourArea(contour) > 5:  # Filter small contours
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 1)
            cv2.drawContours(binary_image, [contour], -1, (0, 255, 0), 1)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Add width to find the tip # TODO this is only temporary
            tip_x = x + w
            tip_y = y
            detected_candidates.append((tip_x, tip_y))
            cv2.circle(image, (tip_x, tip_y), 1, (255, 0, 0), -1)
    
    # TODO: implement better selection of the relevant positon
    #detected_position = detected_candidates[1] if detected_candidates else (-1, -1)
    detected_position = None

    # TODO implement calulation of probe rotation by using pattern MAYBE?

    if detected_position is None:
        #print("No needle tip detected")
        return binary_image, detected_position, 0
    
    rectangles = [] 
    for contour in contours:
        if cv2.contourArea(contour) > 5:
            x, y, w, h = cv2.boundingRect(contour)
            rectangles.append((x, y))
            
    pixel_distance = np.sqrt((rectangles[0][0] - rectangles[1][0])**2 + (rectangles[0][1] - rectangles[1][1])**2)
    # distance should be equal to 2*10mm = 20mm , white-black
    pixel_size = 20 / pixel_distance # [mm/pixel] # TODO: implement in GUI with input for pattern size

    return binary_image, detected_position, pixel_size

def calculate_detection_error(expected_position, detected_position):
    pixel_error = np.sqrt((expected_position[0] - detected_position[0])**2 + (expected_position[1] - detected_position[1])**2)
    return pixel_error

def crop_coordinate_transform(image, coordinates, top_left):
    x, y = coordinates # coordinates in the cropped image
    crop_x, crop_y = top_left # top left corner of the cropped image in the original image

    x = x + crop_x
    y = y + crop_y
    
    return (x, y)

def draw_probe_tip(image, position):
    if position is not None:
        cv2.circle(image, position, 3, (255, 0, 0), -1)
    return image

# Example usage
if __name__ == "__main__":


    pattern_size = 10 # [mm] black-white-black-white-... pattern size

    #loaded_image = load_image("probe_image.png")
    loaded_image = load_image("probe_image_2.png")

    # Crop the image
    top_left = (792, 319)
    bottom_right = (943, 398) 

    cropped_image = crop_image(loaded_image, top_left, bottom_right)

    # Detect the needle tip
    result_image, detected_position, pixel_size = detect_needle_tip(cropped_image)

    # Show the result 
    show_image(result_image)
    show_image(cropped_image)

    # Transform the detected position to the original image
    detected_position_transformed = crop_coordinate_transform(loaded_image, detected_position, top_left)
    cv2.circle(loaded_image, detected_position_transformed, 3, (255, 0, 0), -1)
    show_image(loaded_image)


    expected_position = (mouse_x, mouse_y)
    pixel_error = calculate_detection_error(expected_position, detected_position)
    mm_error = pixel_error * pixel_size

    print(f"Expected needle tip position: {expected_position}")
    print(f"Detected needle tip position: {detected_position}")
    print(f"Detection pixel_error: {pixel_error} pixels")
    print(f"Detection mm_error: {mm_error} mm")