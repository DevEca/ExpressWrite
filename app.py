from cProfile import run
import os
from flask import Flask, render_template, request, url_for, session, redirect, flash, make_response
from httplib2 import Response
from numpy import size
from werkzeug.utils import secure_filename
from flask import Flask,render_template, request
from fpdf import FPDF
from flaskext.mysql import MySQL
from flask_mysqldb import MySQL
import mysql
import MySQLdb.cursors
import re
import configparser

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "expresswrite"
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['SECRET_KEY'] = " "

mysql = MySQL()
mysql.init_app(app)

#buttons paths:

@app.route('/')
def index():
   return render_template("index.html")

@app.route("/index")
def transagain():
      import os
      if os.path.exists("C:/xampp/htdocs/ExpressWrite/static/img/img_00.png"):
         os.remove("C:/xampp/htdocs/ExpressWrite/static/img/img_00.png")
      return render_template("index.html")

#end of button paths

picFolder = os.path.join('tmp')
app.config['UPLOAD_FOLDER'] = picFolder
base_path = os.path.dirname(__file__)

# Translation Function

@app.route('/textresult', methods = ['POST'])
def upload_file1():
   import os
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      import os
      f.save(os.path.join(base_path + "/" + app.config['UPLOAD_FOLDER'], 'img_00.png'))

      from IPython.display import Image
      from matplotlib import pyplot as plt
      import pandas as pd, numpy as np
      pd.options.display.float_format = ':,.2f'.format

      import warnings
      warnings.simplefilter("ignore")
      
      import os, cv2
      os.chdir(r'C:\xampp\htdocs\ExpressWrite\tmp')

      fileList = [x for x in os.listdir() if 'png' or 'jpg' in x.lower()]
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

# Google CLoud Vision API
   import os
   from google.cloud import vision
   import io
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/xampp/htdocs/ExpressWrite/JSON File/expresswrt-3e0151739efc.json"

   def CloudVisionTextExtractor(handwritings):
      _, encoded_image = cv2.imencode('.png', handwritings)
      content = encoded_image.tobytes()
      image = vision.Image(content=content)
     
      client = vision.ImageAnnotatorClient()
      response = client.document_text_detection(image=image,image_context= {"language_hints": ["en"]})
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
      
# Saving cloud translation into array
   
   y = 0
   listtextCV = []
   
   for m in segments:
    
      handwritings = segments[y]
      response = CloudVisionTextExtractor(handwritings)
      handwrittenText = getTextFromVisionResponse(response)
      listtextCV.append(handwrittenText)
      y = y+1
      

   return render_template('textresult.html', textresultCV = listtextCV) 
   
   
@app.route('/result/pdf', methods = ['GET', 'POST'])
def result():
   result = request.form['texttrans']    

   pdf = FPDF()
   pdf.add_page()
       
   page_width = pdf.w -2 * pdf.l_margin
       
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(page_width, 0.0, 'RESULT TRANSLATION', align='C')
   pdf.ln(10)
       
   pdf.set_font('Courier', '', 12)
       
   col_width = page_width/1
       
   pdf.ln(10)
       
   th = pdf.font_size

      
   pdf.multi_cell(0, 5, result)
   pdf.ln(10)
   
   vowelcounter = len(re.findall('[aeiouAEIOU]', result))
   vowelstring = str(vowelcounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Number of vowels:' + vowelstring)
   pdf.ln(5)

   consonantcounter = len(re.findall('[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZÑñ]', result))
   consonantstring = str(consonantcounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Number of consonants: ' + consonantstring)
   pdf.ln(5)

   uppercasecounter = len(re.findall('[ABCDEFGHIJKLMNOPQRSTUVWXYZÑ]', result))
   uppercasestring = str(uppercasecounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Number of uppercase letters: ' + uppercasestring)
   pdf.ln(5)

   lowercasecounter = len(re.findall('[abcdefghijklmnopqrstuvwxyzñ]', result))
   lowercasestring = str(lowercasecounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Number of lowercase letters: ' + lowercasestring)
   pdf.ln(5)

   lettercounter = len(re.findall('[abcdefghijklmnopqrstuvwxyzñABCDEFGHIJKLMNOPQRSTUVWXYZÑ]', result))
   letterstring = str(lettercounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Total number of letters: ' + letterstring)
   pdf.ln(5)

   numbercounter = len(re.findall('[0123456789]', result))
   numberstring = str(numbercounter)
   pdf.set_font('Times', 'B', 14.0)
   pdf.cell(0,0, 'Total count of numbers: ' + numberstring)
   pdf.ln(5)

   response = make_response(pdf.output(dest='S').encode('latin-1'))
   response.headers.set('Content-Disposition', 'attachment',filename='result.pdf')
   response.headers.set('Content-Type', 'application/pdf')
   return response

@app.route('/offline.html')
def offline():
    return app.send_static_file('offline.html')


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')
 
if __name__ == '__main__':
   app.run(debug = True)
