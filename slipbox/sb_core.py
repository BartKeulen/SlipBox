import os
import fnmatch
import datetime
import subprocess
import pdb
import re

import yaml
import pypandoc as pd

from .sb_config import get_setting, get_sb_dir
from .sb_note import Note
from .sb_utils import id_title_from_filename


def init_slipbox():
    if not os.path.isdir(get_sb_dir()):
        os.makedirs(get_sb_dir())
        os.makedirs(os.path.join(get_sb_dir(), 'notes'))
        os.makedirs(os.path.join(get_sb_dir(), 'attachments'))


def get_all_notes():
    note_ids = []
    titles = []
    notes = []
    for filename in os.listdir(os.path.join(get_sb_dir(), get_setting('notes_path'))):
        note_id, title = id_title_from_filename(filename)
        note_ids.append(note_id)
        titles.append(title)
        notes.append(Note.load(filename=filename))
    return notes, note_ids, titles


def get_new_note_id(notes):
    new_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    all_notes = notes
    for note in all_notes:
        if new_id == note.id:
            print('Found note with same id, try to generate new id')
            return get_new_note_id(notes)
    return new_id


def get_links_in(notes, note):
    links_in = []
    for link_in_note in notes:
        if note.id in link_in_note.linked_notes:
            links_in.append(link_in_note)
    return links_in


def get_children(notes, note):
    children = []
    for child_note in notes:
        if note.id in child_note.parents:
            children.append(child_note)
    return children

def get_tags(notes):
    tags = set()
    for note in notes:
        for tag in note.tags:
            tags.add(tag)
    return tags


def get_notes_with_tag(notes, tag):
    return [note for note in notes if tag in note.tags]


# def generate_html(notes, note=None):
#     generate_index_html(notes)
#     if note:
#         note.generate_html()
#     else:
#         for note in sorted(notes):
#             note.generate_html()




# def generate_pdf(notes, note=None):
#     if note:
#         note.generate_pdf()
#     else:
#         for note in sorted(notes):
#             note.generate_pdf()
    