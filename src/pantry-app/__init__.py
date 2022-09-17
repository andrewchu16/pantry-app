from flask import Flask, render_template
from flask_session import Session
from tempfile import mkdtemp
from . import auth


def create_app(test_config=None):
    # Initialize application
    app = Flask(__name__)

    # Enable template autoreload
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Disable response caching
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Use filesystem instead of signed cookies
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        return render_template("auth/login.html")
    
    return app
    