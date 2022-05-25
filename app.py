from cProfile import run
import os
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)

picFolder = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = picFolder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    logo = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.png')
    return render_template("index.html", user_image = logo)

@app.route('/login')
def login():
    return render_template('login.html')
	
@app.route('/textresult', methods = ['GET', 'POST'])
def upload_file1():
   import os
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'img_00.png'))

      from IPython.display import Image
      from matplotlib import pyplot as plt
      import pandas as pd, numpy as np
      pd.options.display.float_format = ':,.2f'.format

      from google.cloud import vision
      import io

      import warnings
      warnings.simplefilter("ignore")

      import os, cv2
      os.chdir(r'C:\Users\potpo\Desktop\ExpressWrite\uploads')

      fileList = [x for x in os.listdir() if 'png' in x.lower()]
      fileList[:5]

      Image(filename = fileList[0], width = 300)

      img = fileList[0]

      def findHorizontalLines(img):
         img = cv2.imread(img) 
    
    #convert image to greyscale
         gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    # set threshold to remove background noise
         thresh = cv2.threshold(gray,30, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # increase contrast
         pxmin = np.min(img)
         pxmax = np.max(img)
         imgContrast = (img - pxmin) / (pxmax - pxmin) * 255

    #increase line width
         kernel = np.ones((3, 3), np.uint8)
         imgMorph = cv2.erode(imgContrast, kernel, iterations = 1)

    
    # define rectangle structure (line) to look for: width 100, hight 1. This is a 
         horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200,1))
    
    # Find horizontal lines
         lineLocations = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    
         return lineLocations

   lineLocations = findHorizontalLines(img)
   plt.figure(figsize=(24,24))
   plt.imshow(lineLocations, cmap='Greys')

   df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
   df_lineLocations.columns = ['rowLoc', 'LineLength']
   df_lineLocations[df_lineLocations['LineLength'] > 0]

   df_lineLocations['line'] = 0
   df_lineLocations['line'][df_lineLocations['LineLength'] > 100] = 1

   df_lineLocations['cumSum'] = df_lineLocations['line'].cumsum()

   df_lineLocations.head()

   import pandasql as ps

   query = '''
select row_number() over (order by cumSum) as SegmentOrder
, min(rowLoc) as SegmentStart
, max(rowLoc) - min(rowLoc) as Height
from df_lineLocations
where line = 0
--and CumSum !=0
group by cumSum
'''

   df_SegmentLocations  = ps.sqldf(query, locals())
   df_SegmentLocations

   def pageSegmentation1(img, w, df_SegmentLocations):
      img = cv2.imread(img) 
      im2 = img.copy()
      segments = []

      for i in range(len(df_SegmentLocations)):
         y = df_SegmentLocations['SegmentStart'][i]
         h = df_SegmentLocations['Height'][i]

         cropped = im2[y:y + h, 0:w] 
         segments.append(cropped)
         plt.figure(figsize=(8,8))
         plt.imshow(cropped)
         plt.title(str(i+1))        

      return segments

   img = fileList[0]
   w = lineLocations.shape[1]
   segments = pageSegmentation1(img, w, df_SegmentLocations)

    
   import re
   import cv2
   import pytesseract
   from pytesseract import Output
   
   import io
   import os
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/potpo/Desktop/ExpressWrite/JSON File/optical-highway-348907-231d2bf0c1d6.json"

   def CloudVisionTextExtractor(handwritings):
      # convert image from numpy to bytes for submittion to Google Cloud Vision
      _, encoded_image = cv2.imencode('.png', handwritings)
      content = encoded_image.tobytes()
      image = vision.Image(content=content)
      
      # feed handwriting image segment to the Google Cloud Vision API
      client = vision.ImageAnnotatorClient()
      response = client.document_text_detection(image=image)
      
      return response

   def getTextFromVisionResponse(response):
      texts = []
      for page in response.full_text_annotation.pages:
         for i, block in enumerate(page.blocks):  
               for paragraph in block.paragraphs:       
                  for word in paragraph.words:
                     word_text = ''.join([symbol.text for symbol in word.symbols])
                     texts.append(word_text)

      return ' '.join(texts)

   m = 0
   y = 0

   listtextCV = []
   
   for m in segments:
    
      handwritings = segments[y]
      response = CloudVisionTextExtractor(handwritings)
      handwrittenText = getTextFromVisionResponse(response)
      listtextCV.append(handwrittenText)
      y = y+1
   else:
      return render_template('result.html', textresultCV = listtextCV)
 
# tell pytesseract where the engine is installed
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


   def extractTextFromImg(segment):
      text = pytesseract.image_to_string(segment, lang='eng')         
      text = text.encode("gbk", 'ignore').decode("gbk", "ignore")
        
      return text


   n = 0
   x = 0
    
   listtextPT = []
   
   for n in segments:
    
      segment = segments[x]
      text = extractTextFromImg(segment)
      listtextPT.append(text)
      x = x+1
       
   else:
      return render_template('result.html', textresultPT = listtextPT)

  

@app.route("/", methods=['GET', 'POST'])
def transagain():
    if request.method == 'POST':
      return render_template("index.html")
if __name__ == '__main__':
   app.run(debug = True)
