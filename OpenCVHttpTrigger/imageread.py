import cv2
import pytesseract
import re
 
# Mention the installed location of Tesseract-OCR in your system
#pytesseract.pytesseract.tesseract_cmd = 'System_path_to_tesseract.exe'
 
# Read image from which text needs to be extracted
class VinOcr:

    def __init__(self) -> None:
        pass

    def get_vin_number(self, imageFile):
        # img = cv2.imread(imageFile)
        img = imageFile
        
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
            text = pytesseract.image_to_string(cropped)
            recognized_texts.append(text)

        #Apply Regex to get the Vin Number
        pattern =  r"[a-zA-Z0-9]{17}"

        recognized_texts_in_string = ' '.join(recognized_texts)
        #print(recognized_texts_in_string)
        vin_number = re.search(pattern, recognized_texts_in_string).group()

        print(f"Vin Number = {vin_number}")
        return vin_number
    