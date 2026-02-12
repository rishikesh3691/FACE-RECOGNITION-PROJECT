from flask import Flask, render_template, request, redirect, url_for, flash, session
import cv2
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# Create uploads folder
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------------- FACE DETECTION ----------------

def detect_faces(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)

    if image is None:
        return 0

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    return len(faces)

# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT,
image_path TEXT,
faces_detected INTEGER)
""")

conn.commit()
conn.close()

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    conn.close()

    if user:
        session["username"] = username
        return redirect("/upload")

    flash("Invalid Login")
    return redirect("/")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":

        file = request.files["file"]
        path = "uploads/" + file.filename
        file.save(path)

        faces = detect_faces(path)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("UPDATE users SET image_path=?,faces_detected=? WHERE username=?",
                  (path, faces, session["username"]))

        conn.commit()
        conn.close()

        return render_template("results.html",image_path=path,faces_detected=faces)

    return render_template("upload.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
