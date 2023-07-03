# PDF-to-JSON-App
This is a simple application using Python (via PyCharm) and Flask that takes an AWS S3 PDF url as payload, parses the pdf, and returns a .json file download with appropriate sections. Before running the code, the user must be an IAM user with read access to S3 bucket files and set up environmental AWS credential variables in order to successfully run the application.

To set up these environmental variables, follow these instructions:
1) Open the Python Terminal and install the AWS CLI using 'pip install awscli'.
2) Next, configure your credentials: 'aws configure'
3) Then enter your credentials.

Please click the generated link after running the code to download the newly converted .json file.
