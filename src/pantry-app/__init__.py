from venv import create
from flask import Flask, render_template, session, request, flash, redirect
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from . import auth
from . import db
from datetime import date


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

    # Set dollar format
    @app.template_filter('dollar')
    def dollar(s):
        if s:
            return f"${s:,.2f}"
        else:
            return ""

    # Use filesystem instead of signed cookies
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    Session(app)

    def create_list_obj():
        list_obj = dict()
        grocery_lists = db.query_db("SELECT * FROM storages WHERE storage_type=0 AND user_id=:user_id ORDER BY created_date DESC", [session["user_id"]])
        
        for grocery_list in grocery_lists:
            storage_id = grocery_list["storage_id"]
            storage_name = grocery_list["storage_name"]
            created_date = grocery_list["created_date"].date()
            
            items = db.query_db("SELECT * FROM items WHERE storage_id=:storage_id", [storage_id])

            list_obj[storage_name] = dict()
            list_obj[storage_name]["date"] = created_date
            list_obj[storage_name]["list_items"] = items

        return list_obj


    @app.route("/")
    @auth.login_required
    def index():
        users = db.query_db("SELECT * FROM users WHERE user_id = :user_id", [session["user_id"]])

        list_obj = create_list_obj()
        return render_template("index.html", username=users[0]["username"], lists=list_obj)

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
    @auth.login_required
    def logout():
        session.clear()
        return redirect("/")
    
    @app.route("/new-list", methods=["GET", "POST"])
    @auth.login_required
    def new_list():
        if request.method == "POST":
            storage_type = 0 # grocery list type
            storage_name = request.form.get("list-name")

            # create a new list
            db.insert_db("INSERT INTO storages (user_id, storage_type, storage_name) VALUES(?, ?, ?)", 
                session["user_id"], storage_type, storage_name)

            # add new list items 
            num_items = int(request.form.get("num-items"))
            storage_id = db.query_db("SELECT * FROM storages WHERE storage_name = :storage_name", [storage_name])[0]["storage_id"]
            for i in range(1, num_items+1):
                item_name = request.form.get(f"item-name-{i}")
                price = request.form.get(f"item-price-{i}").replace('$', '')
                print(item_name)
                db.insert_db("INSERT INTO items (storage_id, item_name, price) VALUES(?, ?, ?)", storage_id, item_name, price) 
            
            flash(f"{storage_name} created.")
            return redirect("/")
        else:
            unnamed_lists = db.query_db("SELECT * FROM storages WHERE storage_type=0 AND user_id is " +
            ":user_id AND storage_name LIKE 'Grocery-List-%'", [session["user_id"]])
            return render_template("new-list.html", next_list_num=len(unnamed_lists) + 1)

    @app.route("/lists")
    @auth.login_required
    def lists():
        list_obj = create_list_obj()
        return render_template("lists.html", lists=list_obj)

    @app.route("/pantry")
    @auth.login_required
    def pantry():
        pantry = db.query_db("SELECT * FROM storages WHERE user_id = :user_id AND storage_type = 1", [session["user_id"]])
        pantry_name = pantry[0]["storage_name"]
        pantry_id = pantry[0]["storage_id"]
        pantry_items = db.query_db("SELECT * FROM items WHERE storage_id = :storage_id", [pantry_id])
        return render_template("pantry.html", pantry_name=pantry_name, pantry_items=pantry_items) 

    @app.route("/query")
    @auth.login_required
    def query():
        query_type = request.args.get("type")
        item_id = request.args.get("item_id")
        item = db.query_db("SELECT * FROM items WHERE item_id = :item_id", [item_id])
        storage_id = item[0]["storage_id"]

        if query_type == "remove":
            db.insert_db("DELETE FROM items WHERE item_id = :item_id", item_id)
            flash("Item removed.")
        elif query_type == "transfer":
            storage_type = 1  # for pantries
            user = db.query_db("SELECT * FROM users WHERE user_id = :user_id", [session["user_id"]])
            
            user_pantry = db.query_db("SELECT * FROM storages WHERE user_id = :user_id AND storage_type = 1", [session["user_id"]])
            # create a new pantry for the user if they do not have one.
            if len(user_pantry) < 1:
                db.insert_db("INSERT INTO storages (user_id, storage_type, storage_name) VALUES(?, ?, ?)", 
                session["user_id"], storage_type, user[0]["username"] + "'s Pantry")
            db.insert_db("UPDATE items SET storage_id = :storage_id WHERE item_id = :item_id", user_pantry[0]["storage_id"], item_id)
            flash("Item added to your pantry.")
        # remove empty lists
        items_in_list = db.query_db("SELECT * FROM items WHERE storage_id = :storage_id", [storage_id])
        if len(items_in_list) == 0:
            db.insert_db("DELETE FROM storages WHERE storage_id = :storage_id", storage_id)
        return redirect("/")

    return app

    