from flask import Flask, request, jsonify
import boto3, uuid, os

app = Flask(__name__)
s3 = boto3.client('s3', region_name='eu-west-2')
bucket_name = f"cloudguardianai-mvp"

def ensure_bucket_exists(bucket_name: str, region: str = "eu-west-2") -> None:
    # Checks if the bucket exists, creates if missing
    s3 = boto3.client("s3",region_name=region)

    try: 
        existing_bucket = [b["Name"] for b in s3.list_buckets()["Buckets"]]
        if bucket_name not in existing_bucket:
            s3.create_bucket(
                Bucket = bucket_name,
                CreateBucketConfiguration={"LocationConstraint":region}
            )
            print(f"Bucket {bucket_name} created successfully.")
        else:
            print(f"Bucket {bucket_name} already exists")
    except Exception as e:
        print(f"Error check or creating bucket {bucket_name}: {e}")


def analyse_policy(policy: dict) -> dict:
    """
    Analyse the given policy dictionary

    Args: 
    - policy (dict): The policy to analyse.

    Returns:
    - dict: Analysis with risk score, issues, and rewritten policy
    """
    # Validate input
    if not isinstance(policy, dict):
        raise TypeError("policy must be a dict")

    
    # Placeholder for analysis logic
    issues = []
    risk_score = 0
    rewritten_policy = {}

    # Task: Implement analysis logic here
    # Example: detect wildcards, admin access, sensitive services

    return {
        "Risk score": risk_score,
        "Issues" : issues,
        "Rewritten Policy" : rewritten_policy
    }


# Analyse file function
def analyse_file(file_obj):
    text = file_obj.read().decode()
    suspicious = ["malicious","alert"]
    found = [word for word in suspicious if word in text]
    return {"keys found" : found, "status" : "analysed"}

''' Specifies what URL to trigger a specific function
    and specify what kind of HTTP request (GET or POST)'''

@app.route("/upload_and_process",methods=['POST']) 

def upload_and_process():
    if "file" not in request.files:
        return jsonify({"error":"No file uploaded"}),400
    
    file = request.files['file'] # Dictionary-like object that contains all of the files uploaded.
    
    # Find the file size/type
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename): # Validation decision
        return jsonify({"error": "Unsupported file type"}), 400
    
    # Read file in memory (fine for small files, bigger files -> stream)

    try:
        file_bytes = file.read() # read file to memory for analysis and upload
        s3.put_object(
            Bucket=bucket_name,
            Key=f"uploads/{uuid.uuid4()}_{file.filename}",
            Body=file_bytes
            )
    except Exception as e:
        return jsonify({"error": f"Failed to upload file: {e}"}), 500
    
    file.seek(0) # Specifies where to start reading again, 0 the beginning, 10; 10 bytes from the start.
    result = analyse_file(file)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
    
