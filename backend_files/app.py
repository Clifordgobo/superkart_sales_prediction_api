
# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize Flask app with a name
superkart_api = Flask("SuperKart")

# Load the trained model
# Ensure the model filename matches your serialized pipeline
model = joblib.load("best_xgb_full_pipeline.joblib")

# Define a route for the home page
@superkart_api.route('/')
def home():
    return "Welcome to the SuperKart System"

# Define an endpoint to predict sales for a single product
@superkart_api.route('/v1/predict', methods=['POST'])
def predict_sales():
    # Get JSON data from the request
    data = request.get_json()

    # Extract all relevant features from the input data (matching X_raw schema)
    # The full_model_pipeline expects all original raw columns, even those dropped or encoded later.
    # For a robust API, you'd typically define an explicit input schema or Pydantic model.
    # For demonstration, we'll assume the input JSON matches the necessary raw columns.

    # Convert the extracted data into a DataFrame
    # Ensure the order and names of columns match the original training data's raw features.
    # This example assumes the input JSON keys directly map to column names.
    # In a real-world scenario, robust validation and mapping would be crucial.
    input_data = pd.DataFrame([data])

    # Make a prediction using the trained model
    prediction = model.predict(input_data).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Product_Store_Sales_Total': round(prediction, 2)})

# Define an endpoint to predict sales for a batch of products
@superkart_api.route('/v1/predictbatch', methods=['POST'])
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Read the file into a DataFrame. The model pipeline handles preprocessing.
    input_data = pd.read_csv(file)

    # Make predictions for the batch data
    predictions = model.predict(input_data).tolist()

    # Create an output dictionary mapping row indices to predicted sales
    output_list = [{
        "index": i,
        "Predicted_Product_Store_Sales_Total": round(pred, 2)
    } for i, pred in enumerate(predictions)]

    return jsonify(output_list)


# Run the Flask app in debug mode
if __name__ == '__main__':
    # For local development, use debug=True. In production, use a production-ready WSGI server.
    superkart_api.run(debug=True, host='0.0.0.0', port=8080)
