import boto3
from botocore.exceptions import ClientError

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "" # YOUR EMAIL ADDRESS

# Replace recipient@example.com with a "To" address. If your account 
# is still in the sandbox, this address must be verified.
RECIPIENT = "" # YOUR EMAIL ADDRESS

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
# CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "us-east-2"

# The character encoding for the email.
CHARSET = "UTF-8"

BODY_HTML = """<html>
<head></head>
<body>
  <h1>%(body)s</h1>
</body>
</html>
            """ 

def send_email(aws_access_key_id, aws_secret_access_key, subject, body):
    client = boto3.client('ses',region_name=AWS_REGION, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML % vars(),
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        },
        Source=SENDER,
        # If you are not using a configuration set, comment or delete the
        # following line
        #ConfigurationSetName=CONFIGURATION_SET,
    )
    
    
