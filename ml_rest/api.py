from flask import Blueprint, Flask, request, jsonify
import io
from keras.applications import ResNet50  # pre-built CNN Model
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
import tensorflow as tf
from PIL import Image
import numpy as np


ml_rest_bp = Blueprint("ml_rest", __name__, url_prefix="/ml_rest", template_folder='templates')

model = None


# Function to Load the model
def load_model():
    # global variables, to be used in another function
    global model
    model = ResNet50(weights="imagenet")
    global graph
    graph = tf.get_default_graph()


# Every ML/DL model has a specific format
# of taking input. Before we can predict on
# the input image, we first need to preprocess it.
def prepare_image(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize the image to the target dimensions
    image = image.resize(target)

    # PIL Image to Numpy array
    image = img_to_array(image)

    # Expand the shape of an array,
    # as required by the Model
    image = np.expand_dims(image, axis=0)

    # preprocess_input function is meant to
    # adequate your image to the format the model requires
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image

d_type_headers = {"Content-Type": "application/json"}

@ml_rest_bp.route('/', methods=['GET'])
def index():
    return jsonify({'data': 'return available endpoints and methods'}, 200, d_type_headers)


@ml_rest_bp.route('/predict', methods=["POST"])
def predict():
    load_model()

    data = {}  # dictionary to store result
    data["success"] = False

    # Check if image was properly sent to our endpoint
    if request.method == "POST":
        if request.files.get("image"):
            image = request.files["image"].read()
            image = Image.open(io.BytesIO(image))

            # Resize it to 224x224 pixels
            # (required input dimensions for ResNet)
            image = prepare_image(image, target=(224, 224))

            # Predict ! global preds, results
            with graph.as_default():
                preds = model.predict(image)
                results = imagenet_utils.decode_predictions(preds)
                data["predictions"] = []

            for (ID, label, probability) in results[0]:
                r = {"label": label, "probability": float(probability)}
                data["predictions"].append(r)

            data["success"] = True

    # return JSON response
    return jsonify(data)
