import os
import fnmatch
import datetime
import subprocess
import pdb
import re

import yaml
import pypandoc as pd

from .sb_config import SB_DIR, SETTINGS
from .sb_note import Note


NOTES_DIR = os.path.join(SB_DIR, SETTINGS['notes_path'])
HTML_DIR = os.path.join(SB_DIR, SETTINGS['html_path'])
PDF_DIR = os.path.join(SB_DIR, SETTINGS['pdf_path'])



def init_slipbox():
    if not os.path.isdir(SB_DIR):
        os.makedirs(SB_DIR)
        os.makedirs(os.path.join(SB_DIR, 'notes'))
        os.makedirs(os.path.join(SB_DIR, 'attachments'))


def get_all_notes():
    note_ids = []
    titles = []
    notes = []
    for f in os.listdir(NOTES_DIR):
        note_id, title = f.split('.')[0].split(' - ')
        note_ids.append(note_id)
        titles.append(title)
        notes.append(Note.load(int(note_id), title))
    return note_ids, titles, notes


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


def generate_html(notes, note_id=None):
    generate_index_html(notes)
    if note_id:
        note = Note.load(note_id)
        note.generate_html()
    else:
        for note in sorted(notes):
            note.generate_html()


def generate_index_html(notes):
    md_str = '# Notes\n'
    for note in sorted(notes):
        md_str += '\n- [[{}]] - {}'.format(note.id, note.title)

    filters = ['pandoc-citeproc']
    pdoc_args = ['--mathjax',
                '-s',
                '--metadata=reference-section-title:References',
                '--variable=index:{}'.format(SETTINGS['index']),
                '--variable=pagetitle:{}'.format('Index'),
                '--template={}'.format(os.path.join(SB_DIR, 'template.html')),
                '--bibliography={}'.format(os.path.join(SB_DIR,'bibliography.bib')), 
                '--csl={}'.format(os.path.join(SB_DIR, 'ieee.csl')),
                '--lua-filter={}'.format(os.path.join(SB_DIR, 'fix-links.lua'))]
    outputfile = os.path.join(HTML_DIR, 'index.html')
    pd.convert_text(md_str,
                        to='html5',
                        format='md',
                        outputfile=outputfile,
                        extra_args=pdoc_args,
                        filters=filters)


def generate_pdf(notes, note_id=None):
    if note_id:
        note = Note.load(note_id)
        note.generate_pdf()
    else:
        for note in sorted(notes):
            note.generate_pdf()
    