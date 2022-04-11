from email import message
import cv2
import pytesseract
import re
import numpy as np
import json

# Mention the installed location of Tesseract-OCR in your system
#pytesseract.pytesseract.tesseract_cmd = 'System_path_to_tesseract.exe'
 
# Read image from which text needs to be extracted
class VinOcr:

    def __init__(self) -> None:
        pass

    def get_vin_number(self, image):
        # img = cv2.imread(imageFile)
        img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        
        # Preprocessing the image starts
        
        # Convert the image to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Performing OTSU threshold
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        
        # Specify structure shape and kernel size.
        # Kernel size increases or decreases the area
        # of the rectangle to be detected.
        # A smaller value like (10, 10) will detect
        # each word instead of a sentence.
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        
        # Applying dilation on the threshold image
        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        
        # Finding contours
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                        cv2.CHAIN_APPROX_NONE)
        
        # Creating a copy of image
        im2 = img.copy()

        # Looping through the identified contours
        # Then rectangular part is cropped and passed on
        # to pytesseract for extracting text from it
        # Extracted text is then written into the text file
        recognized_texts = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            #print(f'{x,y,w,h}')
            
            # Drawing a rectangle on copied image
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Cropping the text block for giving input to OCR
            cropped = im2[y:y + h, x:x + w]

            # Apply OCR on the cropped image
            text = pytesseract.image_to_string(cropped, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
            recognized_texts.append(text)
        print(f"recognized_text = {len(recognized_texts)}")
        #return json.dumps(recognized_texts)
        if len(recognized_texts) > 0:
            #Apply Regex to get the Vin Number
            pattern =  r"[a-zA-Z0-9]{17}"

            recognized_texts_in_string = ' '.join(recognized_texts)
            print(f"text in string = {recognized_texts_in_string}")
            matched = re.search(pattern, recognized_texts_in_string)
            if matched:
                vin_number = matched.group()
                print(f"Vin Number = {vin_number}")
                return json.dumps({"vin_number": vin_number, "message": "fetched vin number successfully"})
            else:
                return json.dumps({"vin_number": "", "message": "Vin number not found"})
        else:
            return json.dumps({"message": "Vin number not found"})
    