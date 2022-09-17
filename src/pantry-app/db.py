import sqlite3
import click
from flask import g, current_app

# Modified from: https://flask.palletsprojects.com/en/2.2.x/tutorial/database/

def get_db():
    """Create the database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)

    if db:
        db.close()

def init_db():
    """Initialize the database tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def query_db(query, *args):
    cursor = get_db().cursor()
    results = cursor.execute(query, *args).fetchall()
    cursor.close()

    return results

def insert_db(query, *args):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    db.commit()


@click.command('init-db')
def init_db_command():
    """flask --app pantry-app init-db"""
    init_db()
    click.echo("Database initialized.")