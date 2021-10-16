import re
from types import MethodDescriptorType
import boto3
from boto3.resources.model import Request
from flask import Flask, render_template, session, redirect, sessions, url_for, request, Response, flash
from flask_bootstrap import Bootstrap
from config import S3_BUCKET
from resources import get_bucket, _get_s3_resource, get_bucket_list, s3_client
from filters import datetimeformat



app = Flask(__name__)
Bootstrap(app)
app.secret_key='secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/list1", methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
         buckets = get_bucket_list()
         return render_template("list_buc.html", buckets=buckets)


@app.route("/new_bucket")
def new_bucket():

    return render_template("newbucket.html")

@app.route('/s3_create_bucket', methods=['GET', 'POST'])
def s3_create_bucket():
 
    client = s3_client()
    s3_bucket_create_response = client.create_bucket(Bucket= request.form['name'], CreateBucketConfiguration={'LocationConstraint': 'us-west-1'})
    
    flash('New Bucket created successfully')
    return redirect(url_for('user'))

@app.route('/empty_bucket', methods=['POST'])
def empty_bucket():
    my_bucket = get_bucket()
    my_bucket.objects.all().delete()

    flash('Bucket has been emptied successfully')
    return redirect(url_for('user'))

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    my_bucket = get_bucket()
    my_bucket.delete()

    flash('Bucket deleted successfully')
    return redirect(url_for('user'))

@app.route("/files")
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('files'))

@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

if __name__ == "__main__":
    app.run()
