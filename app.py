from flask import Flask, render_template, request
import os
import uuid

app = Flask(__name__)
IMAGES_DIR = os.path.join(os.getcwd(), "images")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploadImage", methods=["POST"])
def upload_image():
    if request.files:
        image_file = request.files.get('imageToUpload', '')
        image_name = image_file.filename
        image_extension = os.path.splitext(image_name)[1]
        image_uuid = str(uuid.uuid4())
        new_image_filename = image_uuid + image_extension
        image_file.filename = new_image_filename
        print(image_file)
        image_file.save(IMAGES_DIR)
        
    return "Done"

if __name__ == "__main__":
    app.run()
