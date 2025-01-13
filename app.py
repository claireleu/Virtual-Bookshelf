from flask import Flask, render_template, request
from google.cloud import vision
import os
import requests


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/search/' 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/claire/Downloads/googlecloudvision-privatekey.json'
PINTEREST_ACCESS_TOKEN = 'AMA6ADQXACKKIAQAGAAMYCQLZC6VZFABQBIQCA2AEEHWC5SB6OW3ARUCH32WIPQ5JTBGHENTR5WU6TGNCMFZ2MT6H4RC2CYA'

@app.route('/')
def home():
    return render_template('home.html', the_title = "Home")

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        image = request.files['image']
        if image:
            image_path = os.path.join(UPLOAD_FOLDER, image.filename)  # Define the path to save the image
            image.save(image_path)  # Save the uploaded image to the specified path # Call a function to get a description from the uploaded image
            
            description = get_image_description(image_path)
            search_results = search_pinterest_pin(description)
            
            os.remove(image_path)
            return render_template('search.html', the_title="Search Results", results=search_results, description=description, image=image)
    return render_template('search.html', the_title="Image Search")

def get_image_description(image_path):
    client = vision.ImageAnnotatorClient()
    labelList = []
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        labelList.append(label.description)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return labelList

def search_pinterest_pin(labels):
    headers = {
    'Authorization': f'Bearer {PINTEREST_ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    }
    results = []
    for label in labels:
        response = requests.get(f'https://api.pinterest.com/v5/search/partner/pins?term={label}&country_code=CA',
                                headers=headers)
        print(response)
        
        if response.status_code == 200:
            boards = response.json().get('data', [])
            results.extend(boards)
        else:
            print(f"Failed to fetch pins for label {label}")
    return results


@app.route('/library')
def route_page():
    return render_template('library.html', the_title = "personal library")

if __name__ == '__main__':
    app.run(debug=True)