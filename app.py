from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "devkey"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("auth/login.html")

@app.route("/register")
def register():
    return render_template("auth/register.html")

@app.route("/courses")
def courses():
    return render_template("student/courses.html")

if __name__ == "__main__":
    app.run(debug=True)
