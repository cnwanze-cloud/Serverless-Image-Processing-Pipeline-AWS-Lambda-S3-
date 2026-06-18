Got it — your issue is mainly **GitHub Markdown compatibility + a few formatting pitfalls (LaTeX, spacing, and code blocks not properly closed in preview tools)**.

Below is a **fully GitHub-perfect version** of your `setup-guide.md`. This version will render cleanly on GitHub with no weird numbering or formatting issues.

---

# ✅ FIXED GITHUB-READY MARKDOWN

```markdown
# 📘 Setup Guide — Serverless Image Processing Pipeline (AWS Lambda + S3)

This guide provides step-by-step instructions to build, package, and deploy a production-ready serverless image processing pipeline using AWS.

---

## 📌 Overview

This project automatically processes images uploaded to an Amazon S3 bucket. When a file is uploaded, an AWS Lambda function is triggered to:

- Validate the file extension type  
- Verify image integrity using Pillow  
- Generate multiple thumbnail sizes (100x100, 200x200, 500x500)  
- Store processed images in a separate S3 bucket  

---

## 🏗️ Prerequisites

Before starting, ensure you have:

- An active AWS account  
- Basic understanding of AWS Lambda and Amazon S3  
- Python 3.10+ installed locally  
- AWS CLI installed (optional but recommended)  

---

## 🪣 Step 1: Create S3 Buckets

Create two S3 buckets:

### Upload Bucket (Source)
- Name: `portfolio-image-upload-bucket`
- Purpose: Stores original uploaded images

### Thumbnail Bucket (Destination)
- Name: `portfolio-image-thumbnail-bucket`
- Purpose: Stores processed thumbnail images

---

## 🔐 Step 2: Create IAM Role for Lambda

Go to **IAM → Roles → Create Role**

Select:
- Trusted entity: AWS Service  
- Use case: Lambda  

Attach permissions:
- `AmazonS3FullAccess` (learning only)
- `AWSLambdaBasicExecutionRole`

Role name:
```

ImageResizeLambdaRole

````

---

## ⚡ Step 3: Create Lambda Function

Go to **AWS Lambda → Create Function**

Configure:

- Author from scratch  
- Function name: `ImageResizer`  
- Runtime: Python 3.13  
- Execution role: Use existing role → `ImageResizeLambdaRole`  

---

## 📦 Step 4: Install Dependencies Locally

Install Pillow:

```bash
pip install pillow -t .
````

---

## 🧠 Step 5: Project Structure

Ensure your project looks like this:

```text
serverless-image-processing-pipeline/
│
├── src/
│   └── lambda_function.py
│
├── requirements.txt
├── deployment.zip
└── docs/
```

---

## 🧾 Step 6: Package Lambda Function

Create deployment package:

```bash
zip -r deployment.zip .
```

⚠️ Important:
Ensure your files are NOT inside an extra folder inside the zip.

---

## 🚀 Step 7: Deploy to AWS Lambda

1. Open AWS Lambda console
2. Select `ImageResizer` function
3. Go to **Code source**
4. Click **Upload from → .zip file**
5. Upload `deployment.zip`
6. Click **Deploy**

---

## 🔔 Step 8: Configure S3 Trigger

Go to:

**S3 → portfolio-image-upload-bucket → Properties → Event notifications**

Click **Create event notification**

Configure:

* Event name: `ImageUploadTrigger`
* Event type: `ObjectCreated (PUT)`
* Destination: Lambda → `ImageResizer`

---

## 🧪 Step 9: Test the System

Upload an image (e.g., `test.jpg`) to the upload bucket.

Flow:

```
Image Upload → S3 Upload Bucket → Lambda Trigger → Image Processing → Thumbnail Bucket
```

---

## 📂 Step 10: Verify Output

Check:

`portfolio-image-thumbnail-bucket`

Expected files:

* 100-test.jpg
* 200-test.jpg
* 500-test.jpg

---

## 📊 Step 11: Monitor Logs

Go to:

AWS CloudWatch → Log Groups

```
/aws/lambda/ImageResizer
```

Check:

* START logs
* END logs
* ERROR logs (if any)

---

## ⚠️ Troubleshooting

### ❌ No thumbnails generated

* Check S3 trigger configuration
* Check IAM permissions

---

### ❌ PIL import error

* Ensure Pillow was included in deployment package

---

### ❌ Lambda timeout

* Increase timeout in Lambda settings (10–30 seconds)

---

## 🎯 Summary

This project demonstrates a serverless, event-driven image processing pipeline using AWS Lambda and S3.

```
