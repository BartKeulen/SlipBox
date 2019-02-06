import os
import datetime
import subprocess
import pdb
import re

import yaml


SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SB_DIR = os.path.join(os.path.expanduser('~'), '.slipbox')
NOTES_DIR = os.path.join(SB_DIR, 'notes')
NOTE_TYPES = ['Inbox', 'Archive', 'Reference']


class Note:

    def __init__(self, id, title, date, last_updated=None, tags=None, project=None, parents=None, note_type=None, content=None, bibkey=None):
        self.id = id
        self.title = title
        self.date = date
        self.last_updated = last_updated if last_updated else date
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
        note_fp = os.path.join(NOTES_DIR, '{}.md'.format(self.id))

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
            outfile.write('title: {}\n'.format(self.title))
            outfile.write('date: {}\n'.format(self.date.strftime("%Y-%m-%d %H:%M:%S")))
            outfile.write('last updated: {}\n'.format(last_updated.strftime("%Y-%m-%d %H:%M:%S")))
            outfile.write('tags: {}\n'.format(tags))
            outfile.write('project: {}\n'.format(project))
            outfile.write('parents: {}\n'.format(parents))
            outfile.write('type: {}\n'.format(note_type))
            if note_type is 'Reference':
                outfile.write('bibkey: {}\n'.format(bibkey))
            outfile.write('---\n\n')
            outfile.write(content)
        self.last_updated = last_updated

        print("Saved note ({}): {}".format(self.id, self.title))

    def get_children(self):
        all_notes = get_all_notes()
        children = []
        for note in all_notes:
            if self.id in note.parents:
                children.append(note)
        return children

    def get_parents(self):
        return [Note.load(parent) for parent in self.parents]

    def get_links_out(self):
        matches = re.findall(r'(\d.md)', self.content)
        return [Note.load(int(f.split('.')[0])) for f in matches]

    def get_links_in(self):
        all_notes = get_all_notes()
        linked_notes = []
        for note in all_notes:
            match = re.search(r'({}.md)'.format(self.id), note.content)
            if match is not None:
                linked_notes.append(note)
        return linked_notes

    @classmethod
    def load(cls, id):
        fp = os.path.join(NOTES_DIR, '{}.md'.format(id))
        if not os.path.isfile(fp):
            print("No note found with id {}".format(id))
            return '{}.md'.format(id)

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

            note = cls(id, title, date, last_updated=last_updated, tags=tags, project=project, parents=parents, note_type=note_type, content=content, bibkey=bibkey)
            return note

    @classmethod
    def create(cls, title, tags=None, project=None, parents=None, note_type=None, content=None, bibkey=None):
        note_id = get_new_note_id()
        date = datetime.datetime.now()
        note = cls(note_id, title, date, tags=tags, project=project, parents=parents, note_type=note_type, content=content, bibkey=bibkey)
        note.save()
        return note

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.id, self.title)

    def __str__(self):
        return '{}:\n id: {}\n title: {}\n date: {}\n last_updated: {}\n tags: {}\n project: {}\n parents: {}\n note_type: {}\n bibkey: {}\n content:\n\n{}'.format(self.__class__.__name__, self.id, self.title, self.date.strftime("%Y-%m-%d %H:%M:%S"), self.last_updated.strftime("%Y-%m-%d %H:%M:%S"), self.tags, self.project, self.parents, self.note_type, self.bibkey, self.content)

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


def get_new_note_id():
    all_notes = get_all_notes()
    cur_id = 0
    for note in all_notes:
        cur_id = note.id if note.id > cur_id else cur_id
    return cur_id + 1


def get_all_notes():
    return [Note.load(int(f.split('.')[0])) for f in os.listdir(NOTES_DIR) if os.path.isfile(os.path.join(NOTES_DIR, f))]


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


def init_slipbox():
    if not os.path.isdir(SB_DIR):
        os.makedirs(SB_DIR)
        os.makedirs(os.path.join(SB_DIR, 'notes'))
        os.makedirs(os.path.join(SB_DIR, 'attachments'))



if __name__ == "__main__":
    # print(get_links_to_note(2))
    note = Note.load(2)
    linkes_out = note.get_links_out()
    print(linkes_out)
    print(note.get_links_in())
    pdb.set_trace()