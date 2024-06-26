import os
from flask import Flask, redirect, request, render_template, url_for, jsonify, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
from test import analyze_image  # test.py dosyasından analyze_image fonksiyonunu içe aktarma
from flask_mysqldb import MySQL
import base64
from math import radians, sin, cos, sqrt, atan2


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'my_secret_key'  # secret key tanımlandı
cors = CORS(app)

UPLOAD_FOLDER = 'uploads'  # Dizin adı düzeltilmiş
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aipotato'

mysql = MySQL(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
    cur = mysql.connection.cursor()
    data = []
    if 'loggedin' in session and session['loggedin']:
        cur.execute("SELECT * FROM all_analysis WHERE analysis_user_id = %s", [session['user_id']])
        data = cur.fetchall()
    cur.close()
    return render_template("upload.html", data=data, username=session.get('username', 'guest'), loggedin=session.get('loggedin', False))


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route('/login_post', methods=['GET', 'POST'])
def login_post():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username=%s AND password=%s', (username, password,))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['user_id'] = record[0]  # Kullanıcı ID'si
            session['username'] = record[1]
            return redirect(url_for("main"))
        else:
            msg = "Incorrect username or password..."
    return render_template("login.html", msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for("main"))

@app.route('/register_post', methods=['GET', 'POST'])
def register_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        country = request.form['country']
        city = request.form['city']
        work = request.form['work']
        mail = request.form['mail']
        cur = mysql.connection.cursor()
        record = cur.execute(f"INSERT INTO user (username, country, city, work, mail, password) VALUES (%s, %s, %s, %s, %s, %s)",
                             (username, country, city, work, mail, password))
        mysql.connection.commit()
        if record:
            session['loggedin'] = True
            session['user_id'] = cur.lastrowid  # Kullanıcı ID'sini alın
            session['username'] = username
            return redirect(url_for("main"))
        cur.close()
        return redirect(url_for("main"))
    return render_template("register.html")

def calculate_distance(lat1, lon1, lat2, lon2):
    # Dünya yarıçapı (km cinsinden)
    R = 6371.0

    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

@app.route('/nearby_analyses', methods=['POST'])
def nearby_analyses():
    if not session.get('loggedin'):
        return jsonify({'error': 'User not logged in'}), 401

    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT analysis_result, latitude, longitude FROM all_analysis WHERE analysis_user_id != %s AND (analysis_result = 'early blight' OR analysis_result = 'late blight')", [session['user_id']])
    data = cur.fetchall()
    cur.close()

    nearby_diseases = []
    for row in data:
        disease, lat, lon = row[0], float(row[1]), float(row[2])
        distance = calculate_distance(latitude, longitude, lat, lon)
        if distance <= 10.0:  # 10 km içinde mi kontrol et
            nearby_diseases.append(disease)

    return jsonify({'nearby_diseases': nearby_diseases})

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

        # Dosyayı base64 formatında kodlayın
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # MIME türünü belirlemek için dosya uzantısını kullanın
            mime_type = f"data:image/{file.filename.rsplit('.', 1)[1].lower()};base64,{encoded_string}"

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

            # Analiz sonucunu veritabanına kaydet
            cur = mysql.connection.cursor()
            analysis_user_id = session.get('user_id', 0)  # Kullanıcı ID'sini session'dan alın (varsayılan olarak 0)
            cur.execute(
                "INSERT INTO all_analysis (analysis_img, analysis_result, analysis_rate, analysis_user_id, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)",
                (mime_type, predicted_class_name, confidence, analysis_user_id, float(latitude), float(longitude))
            )
            mysql.connection.commit()
            cur.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, threaded=True)
