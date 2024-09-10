#!/bin/bash

# Variables (Update these based on your setup)
S3_BUCKET_NAME="recitube.com"  # Your S3 bucket name
BUILD_DIR="public"                     # Directory containing your static website files
AWS_REGION="us-east-1"           # AWS region (e.g., us-west-2)
DISTRIBUTION_ID="your-cloudfront-id"   # CloudFront Distribution ID (if using CloudFront for CDN)

# Step 1: Build the static website (Optional: Adjust if you have a build step)
echo "Building the website..."

npm run build

# Check if the build directory exists
if [ ! -d "$BUILD_DIR" ]; then
  echo "Build directory does not exist. Please ensure you have built your project."
  exit 1
fi

# Step 2: Deploy the website to S3
echo "Deploying website to S3 bucket: $S3_BUCKET_NAME"

# Sync the build directory to the S3 bucket
aws s3 sync $BUILD_DIR s3://$S3_BUCKET_NAME/ --delete

# Step 3: Set S3 bucket for static website hosting (Optional)
echo "Configuring S3 bucket for static website hosting..."
aws s3 website s3://$S3_BUCKET_NAME/ --index-document index.html --error-document error.html

echo "Deployment complete!"