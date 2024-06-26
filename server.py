import os
from flask import Flask, redirect, request, render_template, url_for, jsonify, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
from test import analyze_image  # test.py dosyasından analyze_image fonksiyonunu içe aktarma
from flask_mysqldb import MySQL

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
    user_id = session.get('user_id', 0)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM all_analysis WHERE analysis_user_id = %s", (user_id,))
    data = cur.fetchall()
    cur.close()
    username = session.get('username', 'Guest')
    return render_template("upload.html", data=data, username=username)


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

            # Analiz sonucunu veritabanına kaydet
            cur = mysql.connection.cursor()
            analysis_user_id = session.get('user_id', 0)  # Kullanıcı ID'sini session'dan alın (varsayılan olarak 0)
            cur.execute("INSERT INTO all_analysis (analysis_img, analysis_result, analysis_rate, analysis_user_id) VALUES (%s, %s, %s, %s)",
                        (filename, predicted_class_name, confidence, analysis_user_id))
            mysql.connection.commit()
            cur.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, threaded=True)
