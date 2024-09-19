from flask import Flask, template_rendered, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/registration')
def registration():
    return render_template("registration.html")

@app.route('/login')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run()
