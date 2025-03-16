# Fetch IAM roles and permissions
def fetch_roles(credentials, iam_service):
    roles = []
    project_id = credentials.project_id  # Get project ID from service account
    request = iam_service.projects().roles().list(parent=f"projects/{project_id}")
    response = request.execute()

    for role in response.get("roles", []):
        full_role_name = role["name"]  # This contains "projects/{project_id}/roles/{role_id}"
        
        try:
            role_details = iam_service.projects().roles().get(name=full_role_name).execute()
            roles.append({
                "name": role_details.get("title"),
                "permissions": role_details.get("includedPermissions", []),
            })
        except Exception as e:
            print(f"Error fetching role {full_role_name}: {e}")

    return roles


def fetch_iam_activity_logs(credentials, logging_client):
    project_id = credentials.project_id
    filter_str = f'''
        logName="projects/{project_id}/logs/cloudaudit.googleapis.com%2Factivity"
        AND protoPayload.serviceName="iam.googleapis.com"
    '''

    logs = []
    for entry in logging_client.list_entries(filter_=filter_str):
        payload = entry.payload_json
        if payload:
            # Extract values safely with `.get()`
            auth_info = payload.get("authenticationInfo", {})
            principal_email = auth_info.get("principalEmail", "Unknown")

            authorization_info = payload.get("authorizationInfo", [])
            permission = authorization_info[0].get("permission", "N/A") if authorization_info else "N/A"
            
            resource = payload.get("resourceName", "Unknown")
            method = payload.get("methodName", "Unknown")
            timestamp = entry.timestamp.isoformat()

            # Extract nested fields
            request_info = payload.get("request", {})
            response_info = payload.get("response", {})

            # Extract request details
            private_key_type = request_info.get("private_key_type", "N/A")
            service_account_name = request_info.get("name", "N/A")

            # Extract response details
            valid_after_time = response_info.get("valid_after_time", {}).get("seconds", "N/A")
            valid_before_time = response_info.get("valid_before_time", {}).get("seconds", "N/A")
            key_name = response_info.get("name", "N/A")

            logs.append({
                "user": principal_email,
                "permission": permission,
                "resource": resource,
                "method": method,
                "timestamp": timestamp,
                "private_key_type": private_key_type,
                "service_account_name": service_account_name,
                "valid_after_time": valid_after_time,
                "valid_before_time": valid_before_time,
                "key_name": key_name,
            })
    return logs


# Fetch access logs from Cloud Logging
def fetch_access_logs(credentials, logging_client):
    project_id = credentials.project_id
    filter_str = f'''
        logName="projects/{project_id}/logs/cloudaudit.googleapis.com%2Factivity"
        AND protoPayload.methodName="google.iam.admin.v1.CreateRole"
    '''

    logs = []
    for entry in logging_client.list_entries(filter_=filter_str):
        payload = entry.proto_payload  # ✅ Fix: Use `proto_payload`

        logs.append({
            "user": payload["authenticationInfo"]["principalEmail"],
            "permission": payload["authorizationInfo"][0]["permission"] if "authorizationInfo" in payload else "N/A",
            "resource": payload.get("resourceName", "Unknown"),
            "method": payload.get("methodName", "Unknown"),
            "timestamp": entry.timestamp.isoformat(),
        })
    
    return logs


# Fetch compliance data from BigQuery
def fetch_compliance_data(credentials, bigquery_client):
    project_id = credentials.project_id
    query = f"""
        SELECT status, COUNT(*) as count
        FROM `{project_id}.compliance_dataset.compliance_table`
        GROUP BY status
    """
    query_job = bigquery_client.query(query)
    compliance_data = { "Compliant": 0, "Non-Compliant": 0 }

    for row in query_job.result():  # ✅ Fix: Use `result()`
        compliance_data[row["status"]] = row["count"]
    
    return compliance_data
