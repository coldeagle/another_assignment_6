import json
from datetime import datetime

from barkylib import bootstrap
from barkylib.services import unit_of_work, handlers
from barkylib.adapters.repository import *
from barkylib.domain import commands

# init from dotenv file
from dotenv import load_dotenv
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from .baseapi import AbstractBookMarkAPI


load_dotenv()

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
# db = SQLAlchemy(app)
bus = bootstrap.bootstrap()


class FlaskBookmarkAPI(AbstractBookMarkAPI):
    """
    Flask
    """

    def __init__(self) -> None:
        super().__init__()

    # @app.route("/")
    def index(self):
        return f"Barky API"

    # @app.route("/api/one/<id>")
    def one(self, id):
        try:
            bookmark = handlers.list_bookmark(
                id=id,
                uow=unit_of_work.SqlAlchemyUnitOfWork(),
            )

            if bookmark is None:
                return 'None found', 204
            else:
                return bookmark

        except Exception as e:
            print(e)
            return 'Error', 400

    # @app.route("/api/all")
    def all(self):
        return self.many(filter=None, value=None, sort=None)

    # @app.route("/api/first/<property>/<value>/<sort>")
    def first(self, filter, value, sort):
        bookmarks = self.many(filter, value, sort)
        if bookmarks:
            return bookmarks[0]
        else:
            return bookmarks

    def many(self, filter, value, sort):
        print('many')
        try:
            bookmarks = handlers.list_all_bookmarks(
                filter=filter,
                value=value,
                sort=sort,
                uow=unit_of_work.SqlAlchemyUnitOfWork(),
            )

            if bookmarks is None:
                return 'None found', 204
            else:
                return bookmarks
        except Exception as e:
            print('error!')
            print(e)
            return 'Error', 400

    def add(self, bookmark):
        try:
            handlers.add_bookmark(
                bookmark=bookmark,
                uow=unit_of_work.SqlAlchemyUnitOfWork(),
            )
            return 'OK', 201
        except Exception as e:
            print(e)
            return 'Error', 400

    def add_bookmark(self):
        return self.add(bookmark=self.get_bookmark_from_json(request.get_json(force=True)))

    def delete(self, bookmark):
        try:
            handlers.delete_bookmark(
                bookmark=bookmark,
                uow=unit_of_work.SqlAlchemyUnitOfWork(),
            )

            return 'OK', 201

        except Exception as e:
            print(e)
            return 'Error', 400

    def delete_bookmark(self, id):
        return self.delete(self.one(id=id))

    def update_bookmark(self, id):
        bookmark = self.get_bookmark_from_json(request.get_json(force=True))
        bookmark.id = id
        return self.update(bookmark=bookmark)

    def update(self, bookmark):
        try:
            result = handlers.edit_bookmark(
                bookmark=bookmark,
                uow=unit_of_work.SqlAlchemyUnitOfWork(),
            )
            print(result)
            return 'OK', 201
        except Exception as e:
            print(e)
            return 'Error', 400

    def get_bookmark_from_json(self, req_json) -> Bookmark:
        return Bookmark(
            id=req_json.get('id'),
            title=req_json.get('title'),
            url=req_json.get('url'),
            notes=req_json.get('notes'),
            date_added=req_json.get('date_added'),
            date_edited=datetime.now()
        )


fb = FlaskBookmarkAPI()
bp = Blueprint("flask_bookmark_api", __name__, url_prefix="/api")

# @app.route('/')
bp.add_url_rule("/", "index", fb.index, ["GET"])

# @app.route('/api/one/<id>')
bp.add_url_rule("/one/<id>", "one", fb.one, ["GET"])

# @app.route('/api/all')
bp.add_url_rule("/all", "all", fb.all, ["GET"])

# @app.route('/api/add')
bp.add_url_rule("/add", "add", fb.add_bookmark, methods=["POST"])

# @app.route('/api/edit/<id>')
bp.add_url_rule("/edit/<id>", "edit", fb.update_bookmark, methods=["POST"])

# @app.route('/api/delete/<id>')
bp.add_url_rule("/delete/<id>", "delete", fb.delete_bookmark, methods=["GET"])

# @app.route("/api/first/<filter>/<value>/<sort>")
bp.add_url_rule('/first/<filter>/<value>/<sort>', "first", fb.first, methods=["GET"])