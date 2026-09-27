import streamlit as st
import pandas as pd
import requests # For making HTTP requests to the backend
import json

st.set_page_config(layout="wide")

st.title("SuperKart Sales Prediction Frontend")

st.markdown("--- ")

st.header("Predict Single Product Sales")

with st.form("single_prediction_form"):
    st.write("Enter product details for prediction:")

    # Input fields for product features
    product_id = st.text_input("Product ID", value="FD6114")
    product_weight = st.number_input("Product Weight", value=12.66, format="%.2f")
    product_sugar_content = st.selectbox("Product Sugar Content", ['Low Sugar', 'Regular', 'No Sugar'], index=0)
    product_allocated_area = st.number_input("Product Allocated Area", value=0.027, format="%.3f")
    product_type = st.selectbox("Product Type", [
        'Frozen Foods', 'Dairy', 'Canned', 'Baking Goods', 'Health and Hygiene', 
        'Snack Foods', 'Soft Drinks', 'Household', 'Fruits and Vegetables', 'Meat', 
        'Breads', 'Hard Drinks', 'Breakfast', 'Starchy Foods', 'Seafood', 'Others'
    ], index=0)
    product_mrp = st.number_input("Product MRP", value=117.08, format="%.2f")
    store_id = st.selectbox("Store ID", ['OUT004', 'OUT003', 'OUT001', 'OUT002'], index=0)
    store_establishment_year = st.number_input("Store Establishment Year", value=2009, step=1, format="%d")
    store_size = st.selectbox("Store Size", ['Medium', 'High', 'Small'], index=0)
    store_location_city_type = st.selectbox("Store Location City Type", ['Tier 2', 'Tier 1', 'Tier 3'], index=0)
    store_type = st.selectbox("Store Type", ['Supermarket Type2', 'Departmental Store', 'Supermarket Type1', 'Food Mart'], index=0)

    submitted = st.form_submit_button("Predict Sales")

    if submitted:
        # Construct the payload for the backend API
        payload = {
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

        # Define the backend API URL
        # Use the service name 'backend' and port 7860 as defined in the backend Dockerfile
        # This assumes Docker Compose or Kubernetes networking with service discovery.
        backend_url = "http://backend:7860/v1/predict"
        
        try:
            response = requests.post(backend_url, json=payload)
            if response.status_code == 200:
                prediction_result = response.json()
                st.success(f"Predicted Sales: ${prediction_result['Predicted_Product_Store_Sales_Total']:.2f}")
            else:
                st.error(f"Error from backend: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure the backend service is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("--- ")

st.header("Predict Batch Sales from CSV")

uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    if st.button("Run Batch Prediction"):
        # Define the backend API URL for batch prediction
        batch_backend_url = "http://backend:7860/v1/predictbatch"
        
        try:
            files = {'file': uploaded_file.getvalue()}
            response = requests.post(batch_backend_url, files=files)

            if response.status_code == 200:
                batch_predictions = response.json()
                predictions_df = pd.DataFrame(batch_predictions)
                st.success("Batch predictions completed!")
                st.dataframe(predictions_df)
                
                csv_data = predictions_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Predictions CSV",
                    data=csv_data,
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"Error from backend: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure the backend service is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
