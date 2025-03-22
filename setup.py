import os

def create_project_structure(base_path, structure):
    for path, files in structure.items():
        dir_path = os.path.join(base_path, path)
        os.makedirs(dir_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(dir_path, file)
            open(file_path, 'w').close()  # Create empty file

project_structure = {
    "fraud_detection_system/data/raw": ["transactions.csv", "user_behavior_logs.parquet", "kaggle_credit_card_fraud.csv"],
    "fraud_detection_system/data/processed": ["features.parquet", "fraud_labels.parquet"],
    "fraud_detection_system/data/database": ["fraud_data.duckdb", "fraud_graph.db"],
    "fraud_detection_system/notebooks": ["eda.ipynb", "feature_engineering.ipynb", "model_training.ipynb"],
    "fraud_detection_system/src/data_preprocessing": ["clean_data.py", "feature_store.py", "transform_data.py"],
    "fraud_detection_system/src/models": ["train_isolation_forest.py", "train_xgboost.py", "train_graph_model.py"],
    "fraud_detection_system/src/models/model_registry": ["isolation_forest.pkl", "xgboost_model.json", "graph_anomaly_model.bin"],
    "fraud_detection_system/src/inference": ["predict.py", "fraud_detection_pipeline.py"],
    "fraud_detection_system/src/monitoring": ["drift_detection.py", "model_monitoring.py"],
    "fraud_detection_system/api": ["app.py", "requirements.txt"],
    "fraud_detection_system/api/routers": ["predict.py", "health_check.py"],
    "fraud_detection_system/orchestration": ["flyte_workflows.py", "zenml_pipeline.py"],
    "fraud_detection_system/docker": ["Dockerfile", "docker-compose.yml"],
    "fraud_detection_system/deployment/k8s": ["fraud-detection-deployment.yaml", "fraud-detection-service.yaml", "ingress.yaml"],
    "fraud_detection_system/deployment/containerd": ["config.toml"],
    "fraud_detection_system/security": ["encrypt_data.py", "mask_pii.py", "verify_model_signature.py"],
    "fraud_detection_system/tests": ["test_data_processing.py", "test_models.py", "test_api.py"],
    "fraud_detection_system/config": ["settings.yaml"],
    "fraud_detection_system/scripts": ["download_datasets.py", "train_all_models.py"],
    "fraud_detection_system": [".gitignore", "README.md", "LICENSE"]
}

if __name__ == "__main__":
    base_directory = os.getcwd()
    create_project_structure(base_directory, project_structure)
    print("Project structure created successfully.")
