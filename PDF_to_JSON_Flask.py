import json
import boto3
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from flask import Flask, Response

app = Flask(__name__)
s3 = boto3.client('s3')


# Download pdf from non-public AWS S3 URL. Assumes that IAM user has permission to read s3 bucket files and that
# AWS credential environmental variables are set up. Refer to the README file for more information.
def download_pdf_from_url(url):
    response = requests.get(url)
    file_stream = BytesIO(response.content)
    return file_stream


# Generate a pre-signed S3 URL from appropriate bucket and file. Replace with your bucket name and file key
s3_bucket_name = 'your-bucket-name'
s3_file_key = 'your-file-key'

# Pre-signed S3 URL acts as payload
url = s3.generate_presigned_url('get_object', Params={'Bucket': s3_bucket_name, 'Key': s3_file_key}, ExpiresIn=600)

# Extract text from pdf
pdf_stream = download_pdf_from_url(url)
pdf_file_reader = PdfReader(pdf_stream)


def parse_pdf():
    document_content = ''
    # Parse pdf by page number
    for pg_number in range(len(pdf_file_reader.pages)):
        page = pdf_file_reader.pages[pg_number]
        page_text = page.extract_text()
        document_content += '\n' + page_text

    return document_content


text = parse_pdf()
# Section titles used in samples
sections = ['Title', 'Abstract', 'Keywords', 'Introduction', 'Methods', 'Results', 'Discussion', 'References']


def get_text_after_section_name(text, sections):
    output = []
    # Retrieve title from pdf
    if sections[0] == 'Title':
        try:
            output.append(pdf_file_reader.metadata.title)
        except IndexError:
            output.append('')
    # Retrieve text between section titles
    for i in range(1, len(sections) - 1):
        try:
            start = text.index(sections[i]) + len(sections[i])
            end = text.index(sections[i + 1], start)
            output.append(text[start:end])
        # If section title does not exist in pdf then append nothing to title name
        except ValueError:
            output.append('')
    # 'References' is the last section title for research papers
    # Extract text from 'References' to end of pdf
    if sections[7] == 'References':
        try:
            rest = text.split(sections[7])
            output.append(rest[1])
        except IndexError:
            output.append('')
    return output


section_data = get_text_after_section_name(text, sections)
dict_data = dict(zip(sections, section_data))


# When link clicked, the json file automatically downloads while retaining file name except with .json at end
@app.route('/')
def print_download_json():
    try:
        json_data = json.dumps(dict_data, ensure_ascii=False)
        response = Response(json_data, mimetype='application/json')
        json_file_name = s3_file_key.replace('.pdf', '.json')
        response.headers["Content-Disposition"] = f'attachment; filename = {json_file_name}'
        return response

    except Exception as Error:
        return str(Error), 500


if __name__ == '__main__':
    app.run(port=8000, debug=True)
