from flask import Flask, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import logging, bigquery
from sklearn.ensemble import IsolationForest
import pickle
from google.cloud import storage
import pandas as pd

from src.gcp_data import fetch_iam_activity_logs, fetch_roles
from sample_data.data import RISK_ALERTS, ACCESS_LOGS

app = Flask(__name__)
CORS(app, origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"])

# Path to your GCP service account key file
SERVICE_ACCOUNT_FILE = "../keys/service-account-key.json"

# Initialize GCP clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
iam_service = build("iam", "v1", credentials=credentials)  # Initialize IAM service
logging_client = logging.Client(credentials=credentials)
bigquery_client = bigquery.Client(credentials=credentials)
storage_client = storage.Client(credentials=credentials)

# Fetch IAM roles and permissions
@app.route('/roles', methods=['GET'])
def get_roles():
    roles = fetch_roles(credentials, iam_service)
    
    return jsonify(roles)

# Fetch compliance status (mock data for now)
@app.route('/compliance', methods=['GET'])
def get_compliance():
    project_id = credentials.project_id
    # Query BigQuery for compliance data (example query)
    query = f"""
        SELECT status, COUNT(*) as count
        FROM `{project_id}.compliance_dataset.compliance_table`
        GROUP BY status
    """
    query_job = bigquery_client.query(query)
    compliance_data = { "Compliant": 0, "Non-Compliant": 0 }
    for row in query_job:
        compliance_data[row["status"]] = row["count"]
    return jsonify(compliance_data)

# Fetch risky access patterns from Cloud Logging
@app.route('/risk-alerts', methods=['GET'])
def get_risk_alerts():
    logs = []
    logger = logging_client.logger("iam-access-logs")
    for entry in logger.list_entries():
        logs.append({
            "user": entry.payload.get("user"),
            "permission": entry.payload.get("permission"),
            "timestamp": entry.timestamp,
        })
    return jsonify(RISK_ALERTS)
    return jsonify(logs)

# Load the model from GCP
def load_model_from_gcp():
    bucket = storage_client.get_bucket("iam-governance-ai-model")
    blob = bucket.blob("models/anomaly_detection_model.pkl")
    model = pickle.loads(blob.download_as_string())
    return model

# Fetch predictions from the model
# def detect_anomalies(data):
#     model = load_model_from_gcp()
#     predictions = model.predict(data[["permission_count"]])
#     data["anomaly"] = predictions
#     return data[data["anomaly"] == -1]  # Return only anomalies

# Anomaly detection function
def detect_anomalies(logs):
    # Convert logs to a DataFrame
    df = pd.DataFrame(logs)
    
    # Feature engineering
    df["permission_count"] = df.groupby("user")["permission"].transform("count")
    df["risk_level"] = df["permission"].apply(lambda x: 1 if "delete" in x else 0)  # High-risk permissions
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour  # Extract hour from timestamp
    
    # Train an Isolation Forest model
    model = IsolationForest(contamination=0.3)  # 30% of data is considered anomalous
    df["anomaly"] = model.fit_predict(df[["permission_count", "risk_level", "hour"]])
    
    # Filter anomalies (anomaly == -1)
    anomalies = df[df["anomaly"] == -1].to_dict(orient="records")
    return anomalies

# API endpoint for anomaly detection
@app.route('/detect-anomalies', methods=['GET'])
def get_anomalies():
    # logs = fetch_iam_activity_logs(credentials, logging_client)
    # logs = ACCESS_LOGS
    # data = pd.DataFrame(logs)
    data = ACCESS_LOGS
    # data["permission_count"] = data.groupby("user")["permission"].transform("count")
    anomalies = detect_anomalies(data)
    return jsonify(anomalies)
    return jsonify(anomalies.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100)