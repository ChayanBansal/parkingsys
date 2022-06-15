import sqlite3
import os

import click
from flask import current_app, g
from flask.cli import with_appcontext

from tinydb import TinyDB, Query

"""
Each object in doc db occupancy collection/table represents:
{
    lot_id :{
        VEHICLE_TYPE : {
            "VACANT": [spot_ids,],
            "OCCUPIED": [spot_ids,]
        }
    }
}

"""



def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['RELATIONAL_DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def get_doc_db():
    if 'doc_db' not in g:
        g.doc_db = TinyDB(current_app.config["DOC_DB_PATH"])
    
    return g.doc_db

def close_doc_db(e=None):
    doc_db = g.pop('doc_db', None)

    del doc_db


def init_db():
    
    # Initializing SQLITE DB
    if os.path.exists(current_app.config['RELATIONAL_DB_PATH']):
        os.remove(current_app.config['RELATIONAL_DB_PATH'])
    db = get_db()
    for folders in ["table","scripts"]:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        for subdir, dirs, files in os.walk(os.path.join(os.path.join(current_dir,"sql"),folders)):
            for file in files:
                print(file)
                with open(os.path.join(subdir, file), 'r') as handle:
                    db.executescript(handle.read().strip())
    
    # Initializing TinyDB
    if os.path.exists(current_app.config['DOC_DB_PATH']):
        os.remove(current_app.config['DOC_DB_PATH'])
    
    get_doc_db()
    

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_doc_db)
    app.cli.add_command(init_db_command)