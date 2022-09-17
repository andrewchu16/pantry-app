from flask import Flask, render_template, session, request, flash, redirect
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from . import auth
from . import db


def create_app(test_config=None):
    # Initialize application
    app = Flask(__name__)

    # Disable response caching
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Get configuration information
    app.config.from_pyfile("config.py")

    # Use database
    app.teardown_appcontext(db.close_db)
    app.cli.add_command(db.init_db_command)

    # Use filesystem instead of signed cookies
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    Session(app)


    @app.route("/")
    @auth.login_required
    def index():
        users = db.query_db("SELECT * FROM users WHERE user_id = :user_id", [session["user_id"]])

        return render_template("index.html", username=users[0]["username"])

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log into Pantry app."""
        session.clear()

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            users = db.query_db("SELECT * FROM users WHERE username = :username", [username])

            # check if valid username and password
            if len(users) != 1 or not check_password_hash(users[0]["hash"], password):
                flash("Invalid username/password.")
                return render_template("auth/login.html"), 403

            # remember user is logged in
            session["user_id"] = users[0]["user_id"]

            return redirect("/")
        else:
            return render_template("auth/login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Register for Pantry app."""

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm-password")

            users = db.query_db("SELECT * FROM users WHERE username = :username", [username])

            # check unique username and confirm password
            if len(users) > 0:
                flash("Username already taken.")
                return render_template("auth/register.html"), 403
            elif password != confirm_password:
                flash("Passwords do not match.")
                return render_template("auth/register.html", entered_username=username), 403

            # create new account
            hash = generate_password_hash(password)
            db.insert_db("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

            # remember user is logged in
            users = db.query_db("SELECT * FROM users WHERE username = :username", [username])
            session["user_id"] =  users[0]["user_id"]

            flash("Account successfully registered.")
            return redirect("/")
        else:
            return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")
    
    return app
    