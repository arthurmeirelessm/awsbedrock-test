import boto3

bedrock = boto3.client('bedrock' , 'us-west-2', endpoint_url='https://bedrock.us-west-2.amazonaws.com')
output_text = bedrock.list_foundation_models()
print(output_text)