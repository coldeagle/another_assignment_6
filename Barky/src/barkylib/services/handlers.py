from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Callable, Dict, List, Type

from barkylib.domain import commands, events, models
from barkylib.domain.commands import EditBookmarkCommand
from barkylib.domain.events import BookmarkEdited
from sqlalchemy import select, text

from datetime import datetime

if TYPE_CHECKING:
    from . import unit_of_work


def add_bookmark(
        uow: unit_of_work.AbstractUnitOfWork,
        id: int = None,
        title: str = None,
        url: str = None,
        notes: str = None,
        date_added: datetime = None,
        bookmark: models.Bookmark = None,
):
    date_added = datetime.now()
    if (bookmark is not None and bookmark.date_added is None):
        bookmark.date_added = date_added
    with uow:
        bookmark = models.Bookmark(id=id, title=title, url=url, notes=notes, date_added=date_added, date_edited=datetime.now()) if bookmark is None else bookmark
        uow.bookmarks.add_one(bookmark)


def list_bookmark(
        id: int,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        bookmark = uow.bookmarks.get(id)
        if bookmark is None:
            return 'No results'
        else:
            return json.loads(bookmark.to_json())


def list_all_bookmarks(
        filter: str,
        value: object,
        sort: str,
        uow: unit_of_work.AbstractUnitOfWork
):

    with uow:
        bookmarks = uow.bookmarks.find_all(get_query(filter, value, sort))
        json_bookmarks = list()

        if bookmarks:
            for bookmark in bookmarks:
                json_bookmarks.append(json.loads(bookmark.to_json()))

        return json_bookmarks


def edit_bookmark(
        uow: unit_of_work.AbstractUnitOfWork,
        id: int = None,
        title: str = None,
        url: str = None,
        notes: str = None,
        bookmark: models.Bookmark = None,
):
    with uow:
        try:
            bookmark = models.Bookmark(id=id, title=title, url=url, notes=notes, date_edited=datetime.now()) if bookmark is None else bookmark
            return uow.bookmarks.update(bookmark=bookmark)
        except Exception as e:
            print(e)
            return 'Error', 400


def delete_bookmark(
        bookmark: models.Bookmark,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        try:
            uow.bookmarks.delete_one(bookmark=bookmark)
            return 200
        except Exception as e:
            print(e)
            return 'Error', 400

# def add_bookmark(
#     cmd: commands.AddBookmarkCommand,
#     uow: unit_of_work.AbstractUnitOfWork,
# ):
#     with uow:
#         # look to see if we already have this bookmark as the title is set as unique
#         bookmark = uow.bookmarks.get(title=cmd.title)
#         if bookmark is None:
#             bookmark = models.Bookmark(
#                 cmd.title, cmd.url, cmd.date_added, cmd.date_edited, cmd.notes
#             )
#             uow.bookmarks.add(bookmark)
#         uow.commit()


# ListBookmarksCommand: order_by: str order: str
def list_bookmarks(
    cmd: commands.ListBookmarksCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    bookmarks = None
    with uow:
        bookmarks = uow.bookmarks.all()

    return bookmarks


# DeleteBookmarkCommand: id: int
# def delete_bookmark(
#     cmd: commands.DeleteBookmarkCommand,
#     uow: unit_of_work.AbstractUnitOfWork,
# ):
#     with uow:
#         pass


# EditBookmarkCommand(Command):
# def edit_bookmark(
#     cmd: commands.EditBookmarkCommand,
#     uow: unit_of_work.AbstractUnitOfWork,
# ):
#     with uow:
#         pass


EVENT_HANDLERS = {
    events.BookmarkAdded: [add_bookmark],
    events.BookmarksListed: [list_bookmarks],
    events.BookmarkDeleted: [delete_bookmark],
    events.BookmarkEdited: [edit_bookmark],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.AddBookmarkCommand: add_bookmark,
    commands.ListBookmarksCommand: list_bookmarks,
    commands.DeleteBookmarkCommand: delete_bookmark,
    commands.EditBookmarkCommand: edit_bookmark,
}  # type: Dict[Type[commands.Command], Callable]


def get_query(
        filter: str,
        value: object,
        sort: str
):
    query = select(models.Bookmark)

    if filter is not None:
        if filter == 'id':
            query = query.where(models.Bookmark.id == int(value))
        elif filter == 'title' and isinstance(value, str):
            query = query.where(models.Bookmark.title == str(value))
        elif filter == 'date_added' and isinstance(value, datetime):
            query = query.where(models.Bookmark.date_added == datetime(value))
        elif filter == 'date_edited' and isinstance(value, datetime):
            query = query.where(models.Bookmark.date_edited == datetime(value))

    if sort is not None:
        if sort == 'id':
            query = query.order_by(models.Bookmark.id)
        elif sort == 'title':
            query = query.order_by(models.Bookmark.title)
        elif sort == 'date_added':
            query = query.order_by(models.Bookmark.date_added)
        elif sort == 'date_edited':
            query = query.order_by(models.Bookmark.date_edited)

    return query

