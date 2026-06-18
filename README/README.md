# Serverless Image Processing Pipeline (AWS Lambda + S3)

A professional serverless project demonstrating event-driven architecture, automated media processing, and cloud infrastructure management on AWS. 

This pipeline automatically triggers an AWS Lambda function whenever an image is uploaded to a source Amazon S3 bucket. The function validates the file, generates multiple thumbnail dimensions ($100\times100$, $200\times200$, and $500\times500$), and uploads the resulting assets to a separate destination S3 bucket.

---

## 🏗️ Architecture Diagram
<img width="1408" height="768" alt="Architecture" src="https://github.com/user-attachments/assets/41c674c0-7bb4-46ab-9ec6-fbb22609f431" />


---

## 🛠️ Features & Concepts Learned

* **Event-Driven Architecture:** Decoupled data ingestion and compute using native AWS event bindings.
* **Serverless Compute:** Real-time processing with AWS Lambda using Python 3.13.
* **Object Storage:** Managed object lifecycles using partitioned input and output Amazon S3 buckets.
* **IAM Security:** Fine-grained access control using IAM execution roles with CloudWatch execution permissions.
* **Image Manipulation:** Robust image verification and multi-scale resizing using the `Pillow` library.
* **Observability:** Error handling and telemetry capturing with Amazon CloudWatch Logs.

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Create the Amazon S3 Buckets
1. Open the **AWS Management Console** and navigate to **S3**.
2. Click **Create bucket** and provision two distinct buckets (replace with unique names):
   * **Source Bucket:** `portfolio-image-upload-bucket`
   * **Destination Bucket:** `portfolio-image-thumbnail-bucket`
3. Leave all default settings (blocking public access is recommended) and click **Create bucket**.

### Step 2: Provision the IAM Execution Role
1. Navigate to the **IAM Console** ➔ **Roles** ➔ **Create role**.
2. Select **AWS Service** as the trusted entity type, and choose **Lambda** as the use case.
3. Attach the following managed policies:
   * `AmazonS3FullAccess` *(Note: For production environments, always apply least-privilege principles by restricting access to your specific buckets).*
   * `AWSLambdaBasicExecutionRole` *(Provides permission to write processing logs to Amazon CloudWatch).*
4. Name the role `ImageResizeLambdaRole` and click **Create role**.

### Step 3: Package the Dependencies & Deploy Lambda
Because AWS Lambda does not natively include third-party Python packages like `Pillow`, you must package it alongside your application code.

1. On your local machine, prepare the workspace and target directory:
```bash
   mkdir image-lambda && cd image-lambda
```
2. Install the Pillow library targeting the local directory:
```bash
pip install pillow -t .
```
3. Create a file named lambda_function.py in the root of this folder and paste the application source code provided in the next section.

4. Compress the contents of the entire directory into a deployment package:
```bash
zip -r deployment.zip .
```
5. Navigate to AWS Lambda ➔ Create function ➔ Select Author from scratch.

* Function Name: ImageResizer

* Runtime: Python 3.13

* Execution Role: Choose Use an existing role and select ImageResizeLambdaRole.


6. Click Create function, then navigate to the Code tab, click Upload from, select .zip file, and upload your deployment.zip.

💻 Lambda Function Code
import boto3
import os
from PIL import Image, UnidentifiedImageError

s3 = boto3.client("s3")

DESTINATION_BUCKET = "portfolio-image-thumbnail-bucket"
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

def lambda_handler(event, context):
    try:
        # Extract metadata from the S3 Event payload
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        # 1. File extension validation
        if not key.lower().endswith(ALLOWED_EXTENSIONS):
            print(f"Skipping unsupported file type: {key}")
            return {
                "statusCode": 200,
                "body": f"Skipped unsupported file type: {key}"
            }

        download_path = f"/tmp/{os.path.basename(key)}"

        # Download file from S3 to temporary Lambda environment storage
        s3.download_file(bucket, key, download_path)

        # 2. Structural image validation using Pillow
        try:
            with Image.open(download_path) as test_image:
                test_image.verify()  # Verifies the file integrity
        except UnidentifiedImageError:
            print(f"Invalid or corrupted image file: {key}")
            return {
                "statusCode": 400,
                "body": f"Invalid image file: {key}"
            }

        # 3. Dynamic Thumbnail Generation Loop
        sizes = [100, 200, 500]
        for size in sizes:
            # Re-open image after verification (Pillow requirement)
            with Image.open(download_path) as image:
                image.thumbnail((size, size))
                thumbnail_path = f"/tmp/{size}-{os.path.basename(key)}"
                image.save(thumbnail_path)

                # Upload generated thumbnail to target bucket
                s3.upload_file(
                    thumbnail_path,
                    DESTINATION_BUCKET,
                    f"{size}-{os.path.basename(key)}"
                )
                print(f"Successfully processed and uploaded: {size}-{key}")

        return {
            "statusCode": 200,
            "body": "Thumbnails created successfully"
        }

    except Exception as e:
        print(f"Error processing object {key} from bucket {bucket}: {str(e)}")
        raise e


⚙️ Step 4: Configure the S3 Event Trigger
1 Within your ImageResizer Lambda function console, click Add trigger.

2 Select S3 from the dropdown menu.

3 Select your source bucket: portfolio-image-upload-bucket.

4 For Event type, select All object create events (or PUT).

5 Acknowledge the recursive invocation warning and click Add.

🧪 Testing & Validation
1 Upload a test image (e.g., test.jpg) into your source S3 bucket (portfolio-image-upload-bucket).

2 Navigate to your destination bucket (portfolio-image-thumbnail-bucket). You will see three freshly generated variations:

* 100-landscape.jpg

* 200-landscape.jpg

* 500-landscape.jpg

3 Audit Execution Logs: If an asset fails to appear, open CloudWatch ➔ Log groups ➔ /aws/lambda/ImageResizer to review runtime logs, trace statements, and errors.

🧠 Lessons Learned & Engineering Challenges
* Ephemeral Lambda Storage: AWS Lambda execution contexts are mostly read-only. I learned to leverage the local /tmp directory, which provides writeable storage for runtime file downloading and transformation.

* Pillow Lifecycle Hook: Discovered that Pillow's .verify() function alters the internal file pointer status. To perform thumbnailing actions on the same file wrapper, the image file must be explicitly reopened.
