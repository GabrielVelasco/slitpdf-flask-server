# PDF Splitter Backend

A Flask-based API that handled requests from [this front web page](https://github.com/GabrielVelasco/splitpdf-front). This backend service receives PDF files and splits them into smaller parts based on specified given size, returning the split files as a ZIP (when it works).

## Features and Stuff

- PDF file processing...
- Automatic file size calculation per page (get size of every page in the doc at first... 'get_pages_size()' func)
- Secure file handling (validates file's name and stuff... avoid malicious code :O), unique IDs for each request
- Cross-platform compatibility in theory, works fine on linux at least

## Tech Stack

- Python3.12
- Flask (Web Framework, for creating a server instance)
- PyPDF2 (PDF Processing, for reading/writing PDF files)
- werkzeug (Secure file name)

## API Endpoints

### Split PDF
- **URL**: `/api/split`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `pdf_file`: PDF file to be split (file upload). Don't try uploadng .mp4 or your pc will explode.
  - `max_size`: Maximum size in MB for each split part (int)
- **Response**: ZIP file containing split PDF parts
- **Error Responses**:
  - `400`: Missing or invalid parameters
  - `500`: Server processing error basically

### API is UP?
- **URL**: `/tmp`
- **Method**: `GET`
- **Response**: JSON message if server is alive

## Installation

```bash
# Clone this repo, install dependencies, run: 'python3 app.py' (or try to find how to run a python app on your machine...)
```

## Deployment

Initially deployed to Amazon Elastic Beanstalk, but bc I'm not paying for this, it'll problably be down soon... may migrate in the future (or if web app is working normally, u can 'inspect' the page, go to 'network' tab, listen for request and check which server it's using)

Current deployment URL: `https://pqpmds.us-east-1.elasticbeanstalk.com/tmp`

## Error Handling

- Not at all (for now)

## Security

- It's safer to click on those announcements "naked woman 1km from you"