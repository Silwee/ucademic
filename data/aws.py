import boto3

s3_client = boto3.client("s3",
                         region_name="ap-southeast-1",
                         aws_access_key_id="",
                         aws_secret_access_key="")

bucket_name = "ucademic-images-videos-s3"
cloudfront_url = 'd37u0eh7zt2bro.cloudfront.net/'
