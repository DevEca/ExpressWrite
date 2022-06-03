from cProfile import run
import os
from flask import Flask, render_template, request, url_for, session, redirect, flash
from werkzeug.utils import secure_filename
from flask import Flask,render_template, request
from fpdf import FPDF
from flaskext.mysql import MySQL
from flask_mysqldb import MySQL
import mysql
import MySQLdb.cursors
import re


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

@app.route('/user_image')
def index():
    logo = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.png')
    return render_template("index.html", user_image = logo)

@app.route('/')
def index1():
    logo = os.path.join(app.config['UPLOAD_FOLDER'], 'logo.png')
    return render_template("index.html", user_image = logo)

@app.route('/logout')
def logout():
   session.pop('name', None)
   #session['loggedin'] = False
   return redirect('/')

@app.route("/transagain")
def transagain():
   if session.get('name'):
      return redirect(url_for('indexuser'))
   else:
      return render_template("index.html")

@app.route('/indexuser')
def indexuser():
   if session.get('name'):
      users = session['name']
      return render_template('indexuser.html', name=users)
   else:
      return redirect(url_for('unauth'))
      
@app.route('/profile')
def profile():
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute('SELECT * FROM user WHERE name = %s', (session['name'],))
   account = cursor.fetchone()
   cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor2.execute("SELECT result_text FROM result_table WHERE user_id = %s", (account['id'],))

   rows = []
   for row in cursor2:
      rows.append(row)
   return render_template('profile.html', account=account, account2=rows)

@app.route('/unauthorized')
def unauth():
    return render_template("unauthorizedacc.html")

#end of button paths

# Login Function    
  
@app.route('/login', methods =['GET', 'POST'])
def login():
   
   if request.method == 'POST':
      name = request.form['username']
      password = request.form['password'].encode('utf-8')
      cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cur.execute("SELECT * FROM user WHERE name = %s AND password = %s", (name, password))
      users = cur.fetchone()
      cur.close()
      if users:
         session['loggedin'] = True
         session['name'] = users['name']
         return redirect(url_for('indexuser', users=users ))
      else:
         error = 'incorrect email/password'
         return render_template('login.html', error=error)
   return render_template('login.html')

# Register Function

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method =='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(name,email,password) VALUES(%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()
        return render_template('successreg.html')
    return render_template('register.html')

picFolder = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = picFolder
	
# Translation Function

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

      import warnings
      warnings.simplefilter("ignore")

      import os, cv2
      os.chdir(r'C:\xampp\htdocs\ExpressWrite\static\img')

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

# Google CLoud Vision API
   import os
   from google.cloud import vision
   import io
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/xampp/htdocs/ExpressWrite/JSON File/expresswrite-dd1b301590f7.json"

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
# Saving cloud translation into array
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
      pass
   
 # Pytesseract  

   import re
   import cv2
   import pytesseract
   from pytesseract import Output

# tell pytesseract where the engine is installed
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


   def extractTextFromImg(segment):
      text = pytesseract.image_to_string(segment, lang='eng')         
      text = text.encode("gbk", 'ignore').decode("gbk", "ignore")
        
      return text

# Saving pytesseract translation into array
   n = 0
   x = 0
    
   listtextPT = []
   
   for n in segments:
    
      segment = segments[x]
      text = extractTextFromImg(segment)
      listtextPT.append(text)
      x = x+1
      
# render both translations on result.html       
   else:
      return render_template('result.html', textresultPT = listtextPT, textresultCV = listtextCV) 

@app.route('/savetrans', methods = ['GET', 'POST'])
def savetrans():
   if session.get('name'):
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM user WHERE name = %s', (session['name'],))
      account = cursor.fetchone()
      transCV =  request.form['texttrans']
      transuserid = account['id']
      cursor.execute("INSERT INTO result_table(result_text, user_id) VALUES(%s, %s)", (transCV, transuserid))
      mysql.connection.commit()
      cursor.close()
      return render_template('savesuccess.html')
   
   else:
      return redirect(url_for('unauth'))

@app.route('/download')
def download_result():
    try:
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      
       cursor.execute("SELECT * FROM result_table")
       result = cursor.fetchall()
       
       pdf = FPDF()
       pdf.add_page()
       
       page_width = pdf.w -2 * pdf.l_margin
       
       pdf.set_font('Times', 'B', 14.0)
       pdf.cell(page_width, 0.0, 'RESULT', align='C')
       pdf.ln(10)
       
       pdf.set_font('Courier', '', 12)
       
       col_width = page_width/4
       
       pdf.ln(1)
       
       th = pdf.font_size
       
       for row in result:
              pdf.cell(col_)
    except Exception as e:
      print(e)
      
    finally:
      cursor.close()
      
if __name__ == '__main__':
   app.run(debug = True)
