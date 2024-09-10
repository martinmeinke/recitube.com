#!/usr/bin/env sh
rm -rf dependencies
rm -f aws_lambda_layer.zip
pip install -t dependencies -r requirements.txt
cd dependencies && zip -r ../aws_lambda_layer.zip . && cd ..
zip aws_lambda_layer.zip -u youtube_recipe.py

aws s3 cp aws_lambda_layer.zip s3://recitube-lambda/aws_lambda_layer.zip



# this might fail if deps are too large!
# weird ssl issues....
# # Create the new function
# aws lambda create-function \
#     --function-name recitube-backend \
#     --runtime python3.10 \
#     --zip-file fileb://aws_lambda_layer.zip \
#     --handler youtube_recipe.handler \
#     --role arn:aws:iam::396195048771:role/recitube-lambda-role \
#     --region us-east-1

# Update the function code
# aws lambda update-function-code \
#     --function-name recitube-backend \
#     --zip-file fileb://aws_lambda_layer.zip \
#     --region us-east-1

aws lambda update-function-code \
  --function-name recitube-backend \
  --s3-bucket recitube-lambda \
  --s3-key aws_lambda_layer.zip

# # Enable function URL
# this might not be fully correct  - creating via web interface worked
# aws lambda create-function-url-config \
#     --function-name recitube-backend \
#     --auth-type NONE \
#     --cors '{"AllowOrigins": ["*"], "AllowMethods": ["*"], "AllowHeaders": ["*"]}' \
#     --region us-east-1

# Optionally, if you want to retrieve the function URL:
aws lambda get-function-url-config \
    --function-name recitube-backend \
    --region us-east-1
