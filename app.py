import os
import tempfile

# Ensure the D:\temp directory exists
if not os.path.exists('D:\\temp'):
    os.makedirs('D:\\temp')

# Set the environment variables in your Flask app
os.environ['TMP'] = 'D:\\temp'
os.environ['TEMP'] = 'D:\\temp'
tempfile.tempdir = 'D:\\temp'

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>File Sharing App</title>
      <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 p-6">
      <div class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <h1 class="text-2xl font-bold mb-4">File Sharing App</h1>
        <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data" class="mb-4">
          <div class="flex items-center">
            <input type="file" name="file" class="border border-gray-300 p-2 rounded mr-2">
            <input type="submit" value="Upload" class="bg-blue-500 text-white px-4 py-2 rounded">
          </div>
        </form>
        <div id="progressContainer" class="hidden mt-4">
          <div class="w-full bg-gray-200 rounded-full">
            <div id="progressBar" class="bg-blue-500 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full" style="width: 0%">0%</div>
          </div>
        </div>
        <h2 class="text-xl font-semibold mb-2">Uploaded Files</h2>
        <ul class="list-disc list-inside">
          {% for file in files %}
            <li>
              <a href="#" onclick="downloadFile('{{ url_for('uploaded_file', filename=file) }}')" class="text-blue-500 hover:underline">{{ file }}</a>
            </li>
          {% endfor %}
        </ul>
        <div id="downloadProgressContainer" class="hidden mt-4">
          <div class="w-full bg-gray-200 rounded-full">
            <div id="downloadProgressBar" class="bg-green-500 text-xs font-medium text-green-100 text-center p-0.5 leading-none rounded-full" style="width: 0%">0%</div>
          </div>
        </div>
      </div>
      <script>
        document.getElementById('uploadForm').addEventListener('submit', function(event) {
          event.preventDefault();
          var form = event.target;
          var formData = new FormData(form);
          var xhr = new XMLHttpRequest();
          xhr.open('POST', form.action, true);
          
          xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
              var percentComplete = (event.loaded / event.total) * 100;
              var progressBar = document.getElementById('progressBar');
              progressBar.style.width = percentComplete + '%';
              progressBar.textContent = Math.round(percentComplete) + '%';
            }
          };
          
          xhr.onloadstart = function() {
            document.getElementById('progressContainer').classList.remove('hidden');
          };
          
          xhr.onloadend = function() {
            document.getElementById('progressContainer').classList.add('hidden');
            if (xhr.status == 200) {
              window.location.reload();
            } else {
              alert('An error occurred!');
            }
          };
          
          xhr.send(formData);
        });

        function downloadFile(url) {
          var xhr = new XMLHttpRequest();
          xhr.open('GET', url, true);
          xhr.responseType = 'blob';

          xhr.onprogress = function(event) {
            if (event.lengthComputable) {
              var percentComplete = (event.loaded / event.total) * 100;
              var downloadProgressBar = document.getElementById('downloadProgressBar');
              downloadProgressBar.style.width = percentComplete + '%';
              downloadProgressBar.textContent = Math.round(percentComplete) + '%';
            }
          };

          xhr.onloadstart = function() {
            document.getElementById('downloadProgressContainer').classList.remove('hidden');
          };

          xhr.onloadend = function() {
            document.getElementById('downloadProgressContainer').classList.add('hidden');
            if (xhr.status == 200) {
              var link = document.createElement('a');
              link.href = window.URL.createObjectURL(xhr.response);
              link.download = url.split('/').pop();
              link.click();
            } else {
              alert('An error occurred!');
            }
          };

          xhr.send();
        }
      </script>
    </body>
    </html>
    ''', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
