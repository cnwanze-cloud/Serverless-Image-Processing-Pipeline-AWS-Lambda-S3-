import boto3
import os
from PIL import Image, UnidentifiedImageError

s3 = boto3.client("s3")

DESTINATION_BUCKET = "portfolio-image-thumbnail-bucket"

# Allowed file types
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def lambda_handler(event, context):

    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        # -----------------------------
        # 1. File extension validation
        # -----------------------------
        if not key.lower().endswith(ALLOWED_EXTENSIONS):
            print(f"Skipping unsupported file type: {key}")
            return {
                "statusCode": 200,
                "body": f"Skipped unsupported file type: {key}"
            }

        download_path = f"/tmp/{os.path.basename(key)}"

        # Download file from S3
        s3.download_file(bucket, key, download_path)

        # -----------------------------------
        # 2. Real image validation (Pillow)
        # -----------------------------------
        try:
            test_image = Image.open(download_path)
            test_image.verify()  # confirms it's a valid image file
        except UnidentifiedImageError:
            print(f"Invalid image file: {key}")
            return {
                "statusCode": 400,
                "body": f"Invalid image file: {key}"
            }

        sizes = [100, 200, 500]

        for size in sizes:

            # Re-open image after verify() (Pillow requirement)
            image = Image.open(download_path)

            image.thumbnail((size, size))

            thumbnail_path = f"/tmp/{size}-{os.path.basename(key)}"

            image.save(thumbnail_path)

            s3.upload_file(
                thumbnail_path,
                DESTINATION_BUCKET,
                f"{size}-{os.path.basename(key)}"
            )

            print(f"Created {size}-{key}")

        return {
            "statusCode": 200,
            "body": "Thumbnails created successfully"
        }

    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        raise