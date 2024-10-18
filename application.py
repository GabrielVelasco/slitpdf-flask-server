from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
import io
import os

application = Flask(__name__) # create the flask app instance (instance name must be 'application' for deploying to beanstalk)

CORS(application)

# set the upload folder 
application.config['UPLOAD_FOLDER'] = 'uploads' # set the upload folder in the app config, so that we can access it later
application.config['OUTPUT_FOLDER'] = 'output'

def get_page_sizes(pdf_reader):
    page_sizes = []

    for page in pdf_reader.pages:
        temp_writer = PdfWriter()
        temp_writer.add_page(page)
        temp_buffer = io.BytesIO()
        temp_writer.write(temp_buffer)
        length = len(temp_buffer.getvalue())
        page_sizes.append(length)

    return page_sizes

def _split_pdf(file_path, part_size_mb):
    """Split a PDF file into parts of a given size. 
    Save parts in the 'output' folder.
    """

    # Create output folder if it doesn't exist
    output_folder = application.config['OUTPUT_FOLDER']
    os.makedirs(output_folder, exist_ok=True)

    # Open the PDF file
    pdf_reader = PdfReader(file_path)
    total_pages = len(pdf_reader.pages)
    total_pages_sum_after = 0

    # Get page sizes
    page_sizes = get_page_sizes(pdf_reader)

    part_size_bytes = part_size_mb * 1024 * 1024  # Convert MB to bytes
    current_part = 1
    current_writer = PdfWriter()
    accumulated_size = 0

    for i, page in enumerate(pdf_reader.pages):
        page_size = page_sizes[i]

        if page_size > part_size_bytes and i == 0:
            current_writer.add_page(page)

        accumulated_size += page_size

        if accumulated_size >= part_size_bytes:
            # Save the current part
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{base_filename}_part_{current_part}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            part_length = len(current_writer.pages)

            with open(output_path, "wb") as output_file:
                current_writer.write(output_file)
                total_pages_sum_after += part_length

            print(f"Saved part #{current_part} with [{part_length}] pages")

            # Start a new part
            current_part += 1

            current_writer = PdfWriter()
            current_writer.add_page(page)

            accumulated_size = page_size

        else:
            current_writer.add_page(page)

    # Save the last part if it's not empty
    if len(current_writer.pages) > 0:
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{base_filename}_part_{current_part}.pdf"
        output_path = os.path.join(output_folder, output_filename)

        part_length = len(current_writer.pages)

        with open(output_path, "wb") as output_file:
            current_writer.write(output_file)
            total_pages_sum_after += part_length

        print(f"Saved part #{current_part} with [{part_length}] pages")

    print(f"PDF split into {current_part} parts.")
    print(f"Original file contains {total_pages} pages. Sum of pages after split: {total_pages_sum_after}")

    if total_pages == total_pages_sum_after:
        return True
    else:
        return False

# Split pdf end point
@application.route('/api/split', methods=['POST'])
def split_pdf():
    """Get 'pdf_file' and'max_size' from the request and split the pdf file"""

    # get info from the request
    pdf_file = request.files['pdf_file']
    max_size = request.form['max_size']

    # do some validation...
    if not pdf_file or not max_size:
        return jsonify({'message': 'Pdf file and max_size are required'}), 400
    
    # max_size must be an int!
    try:
        max_size = int(max_size)
    except ValueError:
        return jsonify({'message': 'max_size must be an integer'}), 400
    
    # save uploaded file to a folder on the server
    os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)
    file_name = secure_filename(pdf_file.filename) # secure the file name so that it's a safe file name (no malicious code)
    file_path = os.path.join(application.config['UPLOAD_FOLDER'], file_name) # using os.path.join to join the folder and the file name (cross-platform)
    
    pdf_file.save(file_path) # save the file to the server, at 'uploads/file_name.pdf'

    # help(pdf_file) // used to see the methods and props available on the file object

    # split the pdf file
    if _split_pdf(file_path, max_size):
        # zip the output folder and send it to the client
        zip_file_name = application.config['OUTPUT_FOLDER'] + '.zip' # name of the zip file
        folder_to_zip = application.config['OUTPUT_FOLDER']  # folder to zip
        
        # zip the 'folder_to_zip' and save it as 'zip_file_name'. 
        # run zip command according to the OS
        if os.name == 'nt':
            os.system(f"tar -a -c -f {zip_file_name} {folder_to_zip}") # windows
        else:
            os.system(f"zip -r {zip_file_name} {folder_to_zip}") # linux/mac

        return send_file(zip_file_name, as_attachment=True)
    
    else:
        return jsonify({'message': 'Failed to split the pdf file'}), 500

@application.route('/tmp', methods=['GET'])
def single_text():
    res = {
        'message': 'Message from the server',
        'another_key': 'another_value'
    }

    return jsonify(res)

if __name__ == '__main__':
    application.run(debug=True)