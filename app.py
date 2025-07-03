from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from pdf2image import convert_from_path
import img2pdf

from config import Config
from models.denoiser import denoise_image

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DENOISED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_old_files():
    now = datetime.now()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['DENOISED_FOLDER']]:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if (now - file_creation_time) > timedelta(hours=app.config['FILE_LIFESPAN_HOURS']):
                    try:
                        os.remove(filepath)
                        print(f"Removed old file: {filepath}")
                    except Exception as e:
                        print(f"Error removing file {filepath}: {e}")

@app.before_request
def before_request_hook():
    cleanup_old_files()

@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.now().year

    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        processed_results = []

        if not files or all(f.filename == '' for f in files):
            flash('No selected file')
            return redirect(request.url)

        for file in files:
            original_file_name = secure_filename(file.filename)
            result_entry = {
                'original_name': original_file_name,
                'status': 'failed',
                'message': 'Unknown error'
            }

            if not allowed_file(original_file_name):
                result_entry['message'] = 'Invalid file type.'
                processed_results.append(result_entry)
                continue

            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > app.config['MAX_FILE_SIZE']:
                result_entry['message'] = f'File size exceeds {app.config["MAX_FILE_SIZE"] / (1024*1024):.0f}MB limit.'
                processed_results.append(result_entry)
                continue

            unique_filename = str(uuid.uuid4()) + os.path.splitext(original_file_name)[1]
            original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            try:
                file.save(original_filepath)
            except Exception as e:
                result_entry['message'] = f"Could not save file: {e}"
                processed_results.append(result_entry)
                continue

            denoised_url = None
            output_type = 'image'
            denoised_previews = []

            if original_file_name.lower().endswith('.pdf'):
                output_type = 'pdf'
                temp_denoised_image_paths = []
                try:
                    images = convert_from_path(original_filepath)

                    for i, image_pil in enumerate(images):
                        image_array = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
                        temp_page_filename = f"{os.path.splitext(unique_filename)[0]}_page_{i}.png"
                        temp_page_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_page_filename)
                        cv2.imwrite(temp_page_filepath, image_array)

                        denoised_array = denoise_image(temp_page_filepath)

                        if denoised_array is not None:
                            temp_denoised_page_filename = f"denoised_{os.path.splitext(unique_filename)[0]}_page_{i}.png"
                            temp_denoised_page_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_denoised_page_filename)
                            cv2.imwrite(temp_denoised_page_filepath, denoised_array)
                            temp_denoised_image_paths.append(temp_denoised_page_filepath)

                            if i < 2:
                                preview_url = url_for('static', filename=f'uploads/{os.path.basename(temp_denoised_page_filepath)}')
                                denoised_previews.append(preview_url)

                        os.remove(temp_page_filepath)

                    if temp_denoised_image_paths:
                        denoised_pdf_filename = f"{os.path.splitext(original_file_name)[0]}_denoised_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                        denoised_pdf_path = os.path.join(app.config['DENOISED_FOLDER'], denoised_pdf_filename)

                        with open(denoised_pdf_path, "wb") as f:
                            f.write(img2pdf.convert(temp_denoised_image_paths))

                        denoised_url = url_for('static', filename=f'denoised/{os.path.basename(denoised_pdf_path)}')
                        result_entry.update({
                            'denoised_url': denoised_url,
                            'output_type': output_type,
                            'status': 'success',
                            'message': 'Processed successfully',
                            'denoised_previews': denoised_previews
                        })
                    else:
                        result_entry['message'] = 'Denoising failed for PDF pages.'

                except Exception as e:
                    result_entry['message'] = f'Error processing PDF: {e}'
                finally:
                    os.remove(original_filepath)
                    for path in temp_denoised_image_paths:
                        if os.path.exists(path):
                            os.remove(path)
            else:
                try:
                    denoised_array = denoise_image(original_filepath)
                    if denoised_array is not None:
                        name, ext = os.path.splitext(original_file_name)
                        denoised_filename = f"{secure_filename(name)}_denoised_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                        denoised_filepath = os.path.join(app.config['DENOISED_FOLDER'], denoised_filename)

                        cv2.imwrite(denoised_filepath, denoised_array)

                        denoised_url = url_for('static', filename=f'denoised/{os.path.basename(denoised_filepath)}')
                        result_entry.update({
                            'denoised_url': denoised_url,
                            'output_type': output_type,
                            'status': 'success',
                            'message': 'Processed successfully'
                        })
                    else:
                        result_entry['message'] = 'Denoising failed.'
                except Exception as e:
                    result_entry['message'] = f'Error processing image: {e}'
                finally:
                    os.remove(original_filepath)

            processed_results.append(result_entry)

        return render_template('index.html', results=processed_results, current_year=current_year)

    return render_template('index.html', results=None, current_year=current_year)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DENOISED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
