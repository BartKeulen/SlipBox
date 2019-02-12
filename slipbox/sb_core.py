import os
import fnmatch
import datetime
import subprocess
import pdb
import re

import yaml
import pypandoc as pd


from .sb_config import SB_DIR, SETTINGS

# SB_DIR = os.path.join(os.path.expanduser('~'), '.slipbox')
NOTES_DIR = os.path.join(SB_DIR, SETTINGS['notes_path'])
HTML_DIR = os.path.join(SB_DIR, SETTINGS['html_path'])
PDF_DIR = os.path.join(SB_DIR, SETTINGS['pdf_path'])
NOTE_TYPES = ['Inbox', 'Index', 'Archive', 'Reference']


class Note:

    def __init__(self, id, title, date, last_updated=None, tags=None, project=None, parents=None, note_type=None, content=None, bibkey=None):
        self.id = id
        self.title = title
        self.date = date if isinstance(date, datetime.date) else datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        last_updated = self.date if last_updated is None else last_updated
        self.last_updated = last_updated if isinstance(last_updated, datetime.date) else datetime.datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
        self.tags = [] if not tags else tags
        self.project = project
        self.parents = [] if not parents else parents
        self.note_type = 'Inbox' if not note_type else note_type
        self.content = content
        self.bibkey = bibkey

        # Check if note_type is valid
        if self.note_type not in NOTE_TYPES:
            raise Exception("{} is not a valid note type. Please choose one of the following: {}".format(note_type, NOTE_TYPES))

        # TODO: Assert if parents exist

    def save(self):
        note_fp = os.path.join(NOTES_DIR, '{} - {}.md'.format(self.id, self.title))

        # Set metadata to empty string or arguments
        tags = '' if not self.tags else self.tags
        project = '' if not self.project else self.project
        parents = '' if not self.parents else self.parents
        note_type = 'Inbox' if not self.note_type else self.note_type
        content = '' if not self.content else self.content
        bibkey = '' if not self.bibkey else self.bibkey

        # Check if note_type is valid
        if note_type not in NOTE_TYPES:
            raise Exception("{} is not a valid note type. Please choose one of the following: {}".format(note_type, NOTE_TYPES))

        # TODO: Assert if parents exist

        last_updated = datetime.datetime.now()
        with open(note_fp, 'w') as outfile:
            outfile.write('---\n')
            outfile.write('title: "{}"\n'.format(self.title))
            outfile.write('date: {}\n'.format(self.date.strftime("%Y-%m-%d %H:%M:%S")))
            outfile.write('last updated: {}\n'.format(last_updated.strftime("%Y-%m-%d %H:%M:%S")))
            outfile.write('tags: {}\n'.format(tags))
            outfile.write('project: "{}"\n'.format(project))
            outfile.write('parents: {}\n'.format(parents))
            outfile.write('type: "{}"\n'.format(note_type))
            if note_type == 'Reference':
                outfile.write('bibkey: "{}"\n'.format(bibkey))
            outfile.write('---\n\n')
            outfile.write(content)
        self.last_updated = last_updated

        print("Saved note: {} - {}".format(self.id, self.title))

    def generate_html(self):
        filters = ['pandoc-citeproc']
        pdoc_args = ['--mathjax', 
                    '-s',
                    '--template={}'.format(os.path.join(SB_DIR, 'template.html')),
                    '--bibliography={}'.format(os.path.join(SB_DIR, 'bibliography.bib')), 
                    '--csl={}'.format(os.path.join(SB_DIR, 'ieee.csl')),
                    '--lua-filter={}'.format(os.path.join(SB_DIR, 'fix-links.lua'))]
        filename = os.path.join(NOTES_DIR, '{}.md'.format(self.id))
        outputfile = os.path.join(HTML_DIR, '{}.html'.format(self.id))
        pd.convert_file(source_file=filename, 
                    to='html5',
                    format='md',
                    outputfile=outputfile,
                    extra_args=pdoc_args,
                    filters=filters)
        print("Generated html for note ({}): {}".format(self.id, self.title))

    def generate_pdf(self):
        filters = ['pandoc-citeproc']
        pdoc_args = ['--mathjax', 
                    '-s',
                    '-V',
                    'geometry:margin=1in',
                    '--bibliography={}'.format(os.path.join(SB_DIR, 'bibliography.bib')), 
                    '--csl={}'.format(os.path.join(SB_DIR, 'ieee.csl')),
                    '--lua-filter={}'.format(os.path.join(SB_DIR, 'fix-links.lua'))]
        filename = os.path.join(NOTES_DIR, '{}.md'.format(self.id))
        outputfile = os.path.join(PDF_DIR, '{}.pdf'.format(self.id))
        pd.convert_file(source_file=filename, 
                    to='pdf',
                    format='md',
                    outputfile=outputfile,
                    extra_args=pdoc_args,
                    filters=filters)
        print("Generated pdf for note ({}): {}".format(self.id, self.title))

    def get_children(self):
        all_notes = get_all_notes()
        children = []
        for note in all_notes:
            if str(self.id) in note.parents:
                children.append(note)
        return sorted(children)

    def get_parents(self):
        parents = [Note.load(parent) for parent in self.parents]
        return sorted(parents)

    def get_links_out(self):
        matches = re.findall(r'\[.*\]\((\d+).md\)', self.content)
        linked_notes = [Note.load(int(f)) for f in matches]
        return sorted(linked_notes)

    def get_links_in(self):
        all_notes = get_all_notes()
        linked_notes = []
        for note in all_notes:
            match = re.search(r'\[.*\]\({}.md\)'.format(self.id), note.content)
            if match is not None:
                linked_notes.append(note)
        return sorted(linked_notes)

    @classmethod
    def load(cls, note_id, title):
        fp = None
        if title is None and note_id is None:
            raise Exception("Please give an id or title")
        elif note_id and title:
            fp = os.path.join(NOTES_DIR, '{} - {}.md'.format(note_id, title))
        elif note_id:
            fs = []
            for f in os.listdir(NOTES_DIR):
                if fnmatch.fnmatch(f, '*{}*.md'.format(note_id)):
                    fs.append(f)
            if len(fs) > 1:
                output_str = 'More than one note found with id {}:'.format(note_id)
                for f in fs:
                    output_str += '\n{}'.format(f)
                    output_str = output_str[:-3]
                print(output_str)
                return None
            elif len(fs) == 1:
                title = fs[0].split('.')[0].split(' - ')[1]
                fp = os.path.join(NOTES_DIR, fs[0])
        elif title:
            fs = []
            for f in os.listdir(NOTES_DIR):
                if fnmatch.fnmatch(f, '*{}*.md'.format(title)):
                    fs.append(f)
            if len(fs) > 1:
                output_str = 'More than one note found with title {}:'.format(title)
                for f in fs:
                    output_str += '\n{}'.format(f)
                    output_str = output_str[:-3]
                print(output_str)
                return None
            elif len(fs) == 1:
                    note_id = int(fs[0].split('.')[0].split(' - ')[0])
                    fp = os.path.join(NOTES_DIR, fs[0])

        if fp is None or not os.path.isfile(fp):
            print("No note found with id {} and title {}".format(note_id, title))
            return None

        with open(fp, 'r') as f:
            tmp = f.read().split('---')

            header = yaml.load(tmp[1])
            title = header['title']
            date = header['date']
            last_updated = header['last_updated'] if 'last_updated' in header else None
            tags = header['tags'] if 'tags' in header else None
            project = header['project'] if 'project' in header else None
            parents = header['parents'] if 'parents' in header else None
            note_type = header['note_type'] if 'note_type' in header else None
            bibkey = header['bibkey'] if 'bibkey' in header else None

            content = '---'.join(tmp[2:]).lstrip()

            note = cls(note_id, title, date, last_updated=last_updated, tags=tags, project=project, parents=parents, note_type=note_type, content=content, bibkey=bibkey)
            return note

    @classmethod
    def create(cls, title, tags=None, project=None, parents=None, note_type=None, content=None, bibkey=None):
        note_id = get_new_note_id()
        date = datetime.datetime.now()
        note = cls(note_id, title, date, tags=tags, project=project, parents=parents, note_type=note_type, content=content, bibkey=bibkey)
        note.save()
        return note

    def __repr__(self):
        return '{} - {}'.format(self.id, self.title)

    def __str__(self):
        return '{}:\n id: {}\n title: {}\n date: {}\n last_updated: {}\n tags: {}\n project: {}\n parents: {}\n note_type: {}\n bibkey: {}\n content:\n\n{}'.format(self.__class__.__name__, self.id, self.title, self.date.strftime("%Y-%m-%d %H:%M:%S"), self.last_updated.strftime("%Y-%m-%d %H:%M:%S"), self.tags, self.project, self.parents, self.note_type, self.bibkey, self.content)

    def __cmp__(self, other):
        if hasattr(other, 'id'):
            if type(other.id) is not int:
                other_id = int(other.id)
            else:
                other_id = other.id

            if self.id < other_id:
                return -1
            else:
                return 1
        else:
            return 1

    def print_links(self):
        links_out = self.get_links_out()
        links_in = self.get_links_in()

        output_str = 'Links in:\n'
        for link in links_in:
            output_str += ' - {}\n'.format(repr(link))
        output_str += '\nLinks out:\n'
        for link in links_out:
            output_str += ' - {}\n'.format(repr(link))
        print(output_str)

    def print_sequence(self):
        children = self.get_children()
        parents = self.get_parents()

        output_str = 'Parents:\n'
        for parent in parents:
            output_str += ' - {}\n'.format(repr(parent))
        output_str += '\nChildren:\n'
        for child in children:
            output_str += ' - {}\n'.format(repr(child))
        print(output_str)

    def show(self):
        print(self)

    def get_fp(self):
        return os.path.join(NOTES_DIR, '{} - {}.md'.format(self.id, self.title))


def get_new_note_id():
    new_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    all_notes = get_all_notes()
    for note in all_notes:
        if new_id == note.id:
            print("Found note with same id, try to generate new id")
            return get_new_note_id()
    return new_id


def get_all_notes():
    notes = []
    for f in os.listdir(NOTES_DIR):
        note_id, title = f.split('.')[0].split(' - ')
        notes.append(Note.load(int(note_id), title))
    return notes


def get_tags():
    tags = set()
    for note in get_all_notes():
        for tag in note.tags:
            tags.add(tag)
    return tags


def get_notes_with_project(project):
    return [note for note in get_all_notes() if project == note.project]


def get_projects():
    projects = set()
    for note in get_all_notes():
        if note.project is not None:
            projects.add(note.project)
    return projects


def get_notes_with_tag(tag):
    return [note for note in get_all_notes() if tag in note.tags]


def generate_html(id=None):
    if id:
        note = Note.load(id)
        note.generate_html()
    else:
        for note in sorted(get_all_notes()):
            note.generate_html()


def generate_pdf(id=None):
    if id:
        note = Note.load(id)
        note.generate_pdf()
    else:
        for note in sorted(get_all_notes()):
            note.generate_pdf()


def init_slipbox():
    if not os.path.isdir(SB_DIR):
        os.makedirs(SB_DIR)
        os.makedirs(os.path.join(SB_DIR, 'notes'))
        os.makedirs(os.path.join(SB_DIR, 'attachments'))

