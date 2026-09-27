
import streamlit as st
import requests
import pandas as pd
import json

# --- Configuration --- #
# This URL will be updated after the backend API is deployed to Cloud Run
# For local testing, replace with your local backend URL, e.g., 'http://localhost:7860'
# Make sure to update this with the actual deployed URL of your backend service
BACKEND_API_URL = "YOUR_BACKEND_API_URL" # Placeholder for deployed backend API URL

# --- Streamlit UI Setup --- #
st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")
st.title("🛒 SuperKart Product Sales Prediction App")
st.markdown("Predict the sales of your SuperKart products using a powerful machine learning model!")

st.sidebar.header("Predict Sales")
prediction_type = st.sidebar.radio("Choose Prediction Type", ("Single Product Prediction", "Batch Prediction (CSV)"))

# --- Single Product Prediction --- #
if prediction_type == "Single Product Prediction":
    st.header("Single Product Sales Prediction")
    st.markdown("Enter product details to get an instant sales forecast.")

    with st.form("single_prediction_form"):
        st.subheader("Product Features")
        product_id = st.text_input("Product ID", "FD3388")
        product_weight = st.number_input("Product Weight (kg)", min_value=0.0, max_value=50.0, value=10.96, step=0.1)
        product_sugar_content = st.selectbox("Product Sugar Content", ['Low Sugar', 'Regular', 'No Sugar'], index=1)
        product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0, value=0.073, format="%.3f")
        product_type = st.selectbox("Product Type", [
            'Dairy', 'Soft Drinks', 'Meat', 'Fruits and Vegetables', 'Household',
            'Baking Goods', 'Snack Foods', 'Frozen Foods', 'Breakfast', 'Health and Hygiene',
            'Hard Drinks', 'Canned', 'Breads', 'Starchy Foods', 'Others', 'Seafood'
        ], index=5)
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=165.12, step=0.01)
        store_id = st.selectbox("Store ID", ['OUT001', 'OUT002', 'OUT003', 'OUT004'], index=0)
        store_establishment_year = st.number_input("Store Establishment Year", min_value=1900, max_value=2025, value=1987, step=1)
        store_size = st.selectbox("Store Size", ['Small', 'Medium', 'High'], index=1)
        store_location_city_type = st.selectbox("Store Location City Type", ['Tier 1', 'Tier 2', 'Tier 3'], index=1)
        store_type = st.selectbox("Store Type", ['Supermarket Type1', 'Supermarket Type2', 'Departmental Store', 'Food Mart'], index=0)

        submitted = st.form_submit_button("Predict Sales")

        if submitted:
            if BACKEND_API_URL == "YOUR_BACKEND_API_URL":
                st.error("**Please update `BACKEND_API_URL` in the `frontend_files/app.py` with your deployed backend service URL.**")
            else:
                # Prepare data as a dictionary
                input_data = {
                    "Product_Id": product_id,
                    "Product_Weight": product_weight,
                    "Product_Sugar_Content": product_sugar_content,
                    "Product_Allocated_Area": product_allocated_area,
                    "Product_Type": product_type,
                    "Product_MRP": product_mrp,
                    "Store_Id": store_id,
                    "Store_Establishment_Year": store_establishment_year,
                    "Store_Size": store_size,
                    "Store_Location_City_Type": store_location_city_type,
                    "Store_Type": store_type
                }

                # Send request to backend API
                try:
                    response = requests.post(f"{BACKEND_API_URL}/v1/predict", json=input_data)
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    prediction_result = response.json()
                    st.success(f"Predicted Sales: **${prediction_result['Predicted_Product_Store_Sales_Total']:.2f}**")
                except requests.exceptions.ConnectionError:
                    st.error(f"Connection Error: Could not connect to the backend API at {BACKEND_API_URL}. Please ensure the backend is running and the URL is correct.")
                except requests.exceptions.Timeout:
                    st.error("Timeout Error: The request to the backend API timed out.")
                except requests.exceptions.HTTPError as err:
                    st.error(f"HTTP Error: {err} - {response.json().get('error', 'An unknown error occurred.')}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

# --- Batch Prediction (CSV) --- #
elif prediction_type == "Batch Prediction (CSV)":
    st.header("Batch Sales Prediction from CSV")
    st.markdown("Upload a CSV file containing multiple product entries to get batch sales predictions.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        if BACKEND_API_URL == "YOUR_BACKEND_API_URL":
            st.error("**Please update `BACKEND_API_URL` in the `frontend_files/app.py` with your deployed backend service URL.**")
        else:
            try:
                # Read the uploaded CSV file
                batch_df = pd.read_csv(uploaded_file)
                st.write("Uploaded data preview:")
                st.dataframe(batch_df.head())

                # Send the CSV file to the backend API
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                response = requests.post(f"{BACKEND_API_URL}/v1/predictbatch", files=files)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                predictions_list = response.json()

                # Convert predictions to DataFrame for display
                predictions_df = pd.DataFrame(predictions_list)
                predictions_df.set_index('index', inplace=True)

                # Merge with original batch_df for a complete view
                results_df = batch_df.copy()
                results_df['Predicted_Product_Store_Sales_Total'] = predictions_df['Predicted_Product_Store_Sales_Total']

                st.success("Batch predictions completed!")
                st.dataframe(results_df)

                csv_output = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Predictions as CSV",
                    data=csv_output,
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                )

            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the backend API at {BACKEND_API_URL}. Please ensure the backend is running and the URL is correct.")
            except requests.exceptions.Timeout:
                st.error("Timeout Error: The request to the backend API timed out.")
            except requests.exceptions.HTTPError as err:
                st.error(f"HTTP Error: {err} - {response.json().get('error', 'An unknown error occurred.')}")
            except pd.errors.EmptyDataError:
                st.error("The uploaded CSV file is empty.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
