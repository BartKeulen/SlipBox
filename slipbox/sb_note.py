# -*- coding: utf-8 -*-
import os
import fnmatch
import datetime
import subprocess
import pdb
import re

import yaml
import pypandoc as pd

from .sb_config import get_sb_dir, get_setting
from .sb_utils import id_title_from_filename


class Note:

    def __init__(self, id, title, date, last_updated=None, tags=None, parents=None, note_type=None, content=None, bibkey=None):
        self.id = id
        self.title = title
        self.date = date if isinstance(
            date, datetime.date) else datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        if last_updated is None:
            self.last_updated = date
        else:
            self.last_updated = last_updated if isinstance(
                last_updated, datetime.date) else datetime.datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
        self.tags = [] if not tags else tags
        self.parents = [] if not parents else parents
        self.note_type = get_setting(
            'default_new_type') if not note_type else note_type
        self.content = content
        self.bibkey = bibkey

        # Check if note_type is valid
        if self.note_type not in get_setting('note_types'):
            raise Exception('{} is not a valid note type. Please choose one of the following: {}'.format(
                note_type, get_setting('note_types')))

        self.linked_notes = map(int, re.findall(
            r'\[\[(\d+)\]\]', self.content)) if self.content else []

        # TODO: Assert if parents exist

    def save(self):
        note_fp = os.path.join(get_sb_dir(), get_setting(
            'notes_path'), '{} - {}.md'.format(self.id, self.title))

        # Set metadata to empty string or arguments
        tags = '' if not self.tags else self.tags
        parents = '' if not self.parents else self.parents
        note_type = 'Inbox' if not self.note_type else self.note_type
        content = '' if not self.content else self.content
        bibkey = '' if not self.bibkey else self.bibkey

        # Check if note_type is valid
        if note_type not in get_setting('note_types'):
            raise Exception('{} is not a valid note type. Please choose one of the following: {}'.format(
                note_type, get_setting('note_types')))

        # TODO: Assert if parents exists
        with open(note_fp, 'w') as outfile:
            outfile.write('---\n')
            outfile.write('id: {}\n'.format(self.id))
            outfile.write('title: "{}"\n'.format(self.title))
            outfile.write('date: {}\n'.format(
                self.date.strftime('%Y-%m-%d %H:%M:%S')))
            outfile.write('updated: {}\n'.format(
                self.last_updated.strftime('%Y-%m-%d %H:%M:%S')))
            outfile.write('tags: {}\n'.format(tags))
            outfile.write('parents: {}\n'.format(parents))
            outfile.write('type: "{}"\n'.format(note_type))
            if note_type == 'Reference':
                outfile.write('bibkey: "{}"\n'.format(bibkey))
            outfile.write('---\n\n')
            outfile.write(content)

        print('Saved note: {} - {}'.format(self.id, self.title))

    def get_parents(self):
        parents = [Note.load(note_id=int(parent)) for parent in self.parents]
        return sorted(parents)

    def get_links_out(self):
        return sorted([Note.load(note_id=int(f)) for f in self.linked_notes])

    @classmethod
    def load(cls, note_id=None, title=None, filename=None):
        if isinstance(note_id, str):
            note_id = int(note_id)
        fp = None
        if filename is None and title is None and note_id is None:
            raise Exception('Please give an id or title')
        elif filename:
            if os.path.isfile(filename):
                fp = filename
            else:
                fp = os.path.join(
                    get_sb_dir(), get_setting('notes_path'), filename)
                if not os.path.isfile(fp):
                    print('No note found with name "{}" on path "{}"'.format(
                        filename, os.path.join(get_sb_dir(), get_setting('notes_path'))))
                    return None
            note_id, title = id_title_from_filename(fp.split('/')[-1])
        elif note_id and title:
            fp = os.path.join(get_sb_dir(), get_setting(
                'notes_path'), '{} - {}.md'.format(note_id, title.encode('ascii', 'ignore')))
            if not os.path.isfile(fp):
                print('No note found with id "{}" and title "{}" on path "{}"'.format(
                    note_id, title, os.path.join(get_sb_dir(), get_setting('notes_path'))))
                return None
        elif note_id:
            fs = []
            for f in os.listdir(os.path.join(get_sb_dir(), get_setting('notes_path'))):
                if fnmatch.fnmatch(f, '*{}*.md'.format(note_id)):
                    fs.append(f)
            if len(fs) > 1:
                output_str = 'More than one note found with id {}:'.format(
                    note_id)
                for f in fs:
                    output_str += '\n{}'.format(f)
                    output_str = output_str[:-3]
                print(output_str)
                return None
            elif len(fs) == 1:
                title = fs[0].split('.')[0].split(' - ')[1]
                fp = os.path.join(
                    get_sb_dir(), get_setting('notes_path'), fs[0])
        elif title:
            fs = []
            for f in os.listdir(os.path.join(get_sb_dir(), get_setting('notes_path'))):
                if fnmatch.fnmatch(f, '*{}*.md'.format(title.encode('ascii', 'ignore'))):
                    fs.append(f)
            if len(fs) > 1:
                output_str = 'More than one note found with title {}:'.format(
                    title)
                for f in fs:
                    output_str += '\n{}'.format(f)
                    output_str = output_str[:-3]
                print(output_str)
                return None
            elif len(fs) == 1:
                note_id = int(fs[0].split('.')[0].split(' - ')[0])
                fp = os.path.join(
                    get_sb_dir(), get_setting('notes_path'), fs[0])

        if fp is None or not os.path.isfile(fp):
            print('No note found with id {} and title {}'.format(note_id, title))
            return None

        with open(fp, 'r') as f:
            tmp = f.read().split('---')

            header = yaml.load(tmp[1])
            title = header['title']
            date = header['date']
            last_updated = header['updated'] if 'updated' in header else None
            tags = header['tags'] if 'tags' in header else None
            parents = header['parents'] if 'parents' in header else None
            note_type = header['type'] if 'type' in header else None
            bibkey = header['bibkey'] if 'bibkey' in header else None

            content = '---'.join(tmp[2:]).lstrip()

            note = cls(note_id, title, date, last_updated=last_updated, tags=tags,
                       parents=parents, note_type=note_type, content=content, bibkey=bibkey)
            return note

    @classmethod
    def create(cls, note_id, title, tags=None, parents=None, note_type=None, content=None, bibkey=None):
        title = title.encode('ascii', 'ignore')
        date = datetime.datetime.now()
        note = cls(note_id, title, date, tags=tags, parents=parents,
                   note_type=note_type, content=content, bibkey=bibkey)
        note.save()
        return note

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__, self.id, self.note_type, self.title)

    def __str__(self):
        return '[{}] {} - {}'.format(self.note_type[0], self.id, self.title)

    def __cmp__(self, other):
        if hasattr(other, 'last_updated'):
            if not isinstance(other.last_updated, datetime.date):
                other_last_updated = datetime.datetime.strptime(other.last_updated, '%Y-%m-%d %H:%M:%S')
            else:
                other_last_updated = other.last_updated

            if self.last_updated > other_last_updated:
                return -1
            else:
                return 1
        else:
            return 1

    def show(self):
        print('{}:\n id: {}\n title: {}\n date: {}\n updated: {}\n tags: {}\n parents: {}\n type: {}\n bibkey: {}\n content:\n\n{}'.format(self.__class__.__name__, self.id,
                                                                                                                                           self.title, self.date.strftime('%Y-%m-%d %H:%M:%S'), self.last_updated.strftime('%Y-%m-%d %H:%M:%S'), self.tags, self.parents, self.note_type, self.bibkey, self.content))

    def get_fp(self, to='notes'):
        if to == 'notes':
            return os.path.join(get_sb_dir(), get_setting('notes_path'), '{} - {}.md'.format(self.id, self.title))
        elif to == 'html':
            return os.path.join(get_sb_dir(), get_setting('html_path'), '{}.html'.format(self.id))
        elif to == 'pdf':
            return os.path.join(get_sb_dir(), get_setting('pdf_path'), '{}.pdf'.format(self.id))
        else:
            print('Cannot get filepath to {}'.format(to))
