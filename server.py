import os
from flask import Flask, redirect, request, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from test import analyze_image  # test.py dosyasından analyze_image fonksiyonunu içe aktarma
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

UPLOAD_FOLDER = 'uploads'  # Dizin adı düzeltilmiş
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'AIPotato'

mysql = MySQL(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM all_analysis")
    data = cur.fetchall()
    cur.close()
    return render_template("upload.html", data=data)

@app.route("/login")
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Konum bilgilerini al
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Görüntüyü analiz et ve sonucu al
        try:
            predicted_class_name, confidence = analyze_image(filepath)
            result = {
                'predicted_class_name': predicted_class_name,
                'confidence': confidence,
                'latitude': latitude,
                'longitude': longitude
            }
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, threaded=True)
