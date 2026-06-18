# S3 Bucket Setup

## Upload Bucket
- Name: portfolio-image-upload-bucket
- Purpose: Stores original images uploaded by users

## Thumbnail Bucket
- Name: portfolio-image-thumbnail-bucket
- Purpose: Stores processed resized images

## Configuration
- Enable event trigger on upload bucket
- Event type: PUT (ObjectCreated)
- Target: AWS Lambda function (ImageResizer)
