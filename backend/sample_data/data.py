RISK_ALERTS = [
    {
        "id": 1,
        "user": "user-1",
        "permission": "storage.buckets.get",
        "timestamp": "2025-03-16T10:00:00Z",
        "riskLevel": "High"
    },
    {
        "id": 2,
        "user": "user-2",
        "permission": "compute.instances.start",
        "timestamp": "2025-03-16T11:00:00Z",
        "riskLevel": "Medium"
    },
    {
        "id": 3,
        "user": "user-3",
        "permission": "bigquery.tables.delete",
        "timestamp": "2025-03-16T12:00:00Z",
        "riskLevel": "Critical"
    }
]


ACCESS_LOGS = [
    {"user": "user-1", "permission": "storage.buckets.get", "timestamp": "2025-03-16T10:00:00Z"},
    {"user": "user-2", "permission": "compute.instances.start", "timestamp": "2025-03-16T11:00:00Z"},
    {"user": "user-3", "permission": "bigquery.tables.delete", "timestamp": "2025-03-16T12:00:00Z"},
    {"user": "user-4", "permission": "storage.buckets.delete", "timestamp": "2025-03-16T13:00:00Z"},  # Anomaly
    {"user": "user-5", "permission": "compute.instances.stop", "timestamp": "2025-03-16T14:00:00Z"},
    {"user": "user-6", "permission": "bigquery.tables.update", "timestamp": "2025-03-16T15:00:00Z"},
    {"user": "user-7", "permission": "storage.buckets.create", "timestamp": "2025-03-16T16:00:00Z"},  # Anomaly
    {"user": "user-8", "permission": "compute.instances.delete", "timestamp": "2025-03-16T17:00:00Z"},  # Anomaly
    {"user": "user-9", "permission": "bigquery.datasets.create", "timestamp": "2025-03-16T18:00:00Z"},
    {"user": "user-10", "permission": "storage.objects.delete", "timestamp": "2025-03-16T19:00:00Z"},  # Anomaly
]