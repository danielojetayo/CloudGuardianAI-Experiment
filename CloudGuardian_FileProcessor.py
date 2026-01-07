from flask import Flask, request, jsonify
import boto3, uuid, os

app = Flask(__name__)
s3 = boto3.client('s3', region_name='eu-west-2')
bucket_name = f"cloudguardianai-mvp"

existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
if bucket_name not in existing_buckets:
    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
                     )
    print("Bucket created successfully")
else:
    print(f"Bucket {bucket_name} already exists, skipping creation.")


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
    if file not in request.files:
        return jsonify({"error":"No file uploaded"}),400
    
    file = request.files['file'] # Dictionary-like object that contains all of the files uploaded.
    file_bytes = file.read() # read file to memory for analysis and upload

    s3.put_object(Bucket=bucket_name,
                Key=f"uplaods/{uuid.uuid4()}_{file.filename}",
                Body=file_bytes
                )
    
    file.seek(0) # Specifies where to start reading again, 0 the beginning, 10; 10 bytes from the start.
    result = analyse_file(file)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
    


'''
s3 = boto3.client('s3', region_name='eu-west-2')

bucket_name = f"cloudguardianai-{uuid.uuid4()}"
print("Creating:", bucket_name)

buckets = s3.list_buckets()['Buckets']

try:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'} 
    ) #Creating a bucket
    print("Bucket created successfully!")
except Exception as e:
    print("Error:", e) 

print("Buckets visible to this user: ")
for b in buckets:
    location = s3.get_bucket_location(Bucket=b["Name"])
    print(b["Name"], "is in", location['LocationConstraint']) #Print all the buckets

s3.put_object(Bucket=bucket_name, 
                Key="test.txt",
                Body="Hello, S3!"
                ) #Uploading a file 
print("File uploaded successfully")

obj = s3.get_object(
    Bucket=bucket_name, 
    Key="test.txt"
    ) #Retrieving a file 
print("File content: ", obj["Body"].read().decode()) #Reading a file
'''
