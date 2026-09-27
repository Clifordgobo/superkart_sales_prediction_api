FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Command to run the Streamlit application
# `--server.port 8501` and `--server.address 0.0.0.0` are crucial for Docker deployments
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
