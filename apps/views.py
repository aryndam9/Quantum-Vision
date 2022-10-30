# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import render_template, request
from flask import Flask, render_template, request, redirect, url_for
from jinja2  import TemplateNotFound

# App modules
from apps import app
# --------------------------------------------
app.config['S3_BUCKET'] = "quantum-tfr"
app.config['S3_KEY'] = "AKIA46YFNGS2I2H55W4U"
app.config['S3_SECRET'] = "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"
app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'.format("quantum-tfr")

import boto3, botocore

s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)

# --------------------------------------------


# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    try:

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template( 'home/' + path, segment=segment )
    
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['image_file']

    if uploaded_file.filename == "":
        return "Please select a file"

    if uploaded_file:
        
        output = send_to_s3(uploaded_file, app.config["S3_BUCKET"])
        obj = s3.get_object(Bucket= app.config["S3_BUCKET"], Key= 'test.txt') 
        # get object and file (key) from bucket
        # print(obj)
        try:
            with open(obj, 'r') as f:
                pred = f.read()
        except:
            pred = 'Yes'
        return render_template('index_update.html')
    else:
        return redirect(url_for('index'))

def send_to_s3(file_img, bucket_name, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3.upload_fileobj(
            file_img,
            bucket_name,
            file_img.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file_img.content_type    #Set appropriate content type as per the file
            }
        )
        print('uploadeed')
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], file_img.filename)

@app.route("/index_update",  methods=['GET', 'POST'])
def index_update():
    return render_template('index_update.html')



