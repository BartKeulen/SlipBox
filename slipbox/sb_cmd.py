import os
import copy
import pdb
import subprocess

import datetime
import click
import click_completion

from .sb_config import *
from .sb_core import *

NOTES_DIR = os.path.join(SB_DIR, SETTINGS['notes_path'])

note_ids, note_titles, all_notes = get_all_notes()

click_completion.init()

@click.group('note')
def cli():
    pass


@click.command()
def init():
    init_sb()


@click.command()
@click.argument('title')
@click.option('-t', '--tag', default=None, multiple=True, type=str, help='tag for note, each tag has to be added separately')
@click.option('-p', '--parent', default=None, multiple=True, type=str, help='parent of note, each parent has to be added separately')
@click.option('-type', '--type', '_type', default=None, type=str, help='Note type')
@click.option('-bib', '--bibkey', default=None, type=str, help='Bibkey of reference')
@click.option('-c', '--content', default=None, type=str, help='Content of Note')
def create(title, tag, parent, _type, bibkey, content):
    global note_ids, note_titles, all_notes
    note_id = get_new_note_id(all_notes)
    tags = [str(t) for t in tag]
    parents = [str(p) for p in parent]
    Note.create(note_id, title, tags, parents, _type, content, bibkey)
    note_ids, note_titles, all_notes = get_all_notes()


@click.command()
@click.option('-id', '--id', '_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str, help='title for note')
@click.option('--update_time', flag_value=True, default=False)
def update(_id, title, update_time):
    global note_ids, note_titles, all_notes
    if _id or title:
        note = Note.load(int(_id), title)
        if update_time:
            note.date = datetime.datetime.now()
        note.save()
    else:
        if update_time:
            print("You can only update the time one note at a time.")
        for note in all_notes:
            note.save()
    note_ids, note_titles, all_notes = get_all_notes()


@click.command()
@click.option('-id', '--id', '_id', default=None, type=click.Choice(note_ids))
@click.option('-title', '--title', default=None, type=str)
def edit(_id, title):
    note = Note.load(int(_id), title)
    if note:
        subprocess.call(['editor', note.get_fp()])


@click.command()
@click.option('-a', '--al', '_all', flag_value=True, default=False)
@click.option('-t', '--tag', multiple=True, default=None, type=str, help='tag for note, each tag has to be added separately')
@click.option('--type', '-type', '_type', default=None, type=click.Choice(SETTINGS['note_types']), multiple=True)
def notes(_all, tag, _type):
    notes = copy.deepcopy(all_notes)
    
    if not _all:
        _notes = []
        if not _type:
            _type = (SETTINGS['default_view_type'], )

        for note in notes:
            if note.note_type in _type:
                _notes.append(note)
        notes = _notes
                
        tags = [str(t) for t in tag]
        if tags:
            _notes = []
            for note in notes:
                for _tag in tags:
                    if _tag in note.tags:
                        _notes.append(note)
            notes = _notes
    
    # Sort notes on id
    notes = sorted(notes)

    # output_str = 'Notes:\n'
    output_str = ''
    for note in notes:
        output_str += '{}\n'.format(repr(note))

    print(output_str[:-1])


@click.command()
@click.option('-id', '--id', '_id', default=None, type=click.Choice(note_ids))
@click.option('-title', '--title', default=None, type=click.Choice(note_titles))
def links(_id, title):
    note = Note.load(int(_id), title)
    links_out = note.get_links_out()
    links_in = get_links_in(all_notes, note)

    output_str = 'Links in:\n'
    for link in links_in:
        output_str += '  {}\n'.format(repr(link))
    output_str += '\nLinks out:\n'
    for link in links_out:
        output_str += '  {}\n'.format(repr(link))
    print(output_str)

@click.command()
@click.option('-id', '--id', '_id', default=None, type=click.Choice(note_ids))
@click.option('-title', '--title', default=None, type=click.Choice(note_titles))
def sequence(_id, title):
    note = Note.load(int(_id), title)
    parents = note.get_parents()
    children = get_children(all_notes, note)

    output_str = 'Parents:\n'
    for parent in parents:
        output_str += '  {}\n'.format(repr(parent))
    output_str += '\nChildren:\n'
    for child in children:
        output_str += '  {}\n'.format(repr(child))
    print(output_str)


@click.command()
@click.option('-id', '--id', '_id', default=None, type=click.Choice(note_ids))
@click.option('-title', '--title', default=None, type=click.Choice(note_titles))
def show(_id, title):
    note = Note.load(int(_id), title)
    note.show()


@click.command()
def tags():
    tags = get_tags(all_notes)
    # output_str = 'Tags:\n'
    output_str = ''
    for tag in tags:
        output_str += '{}\n'.format(tag)
    print(output_str[:-1])


@click.command()
@click.option('--id', '-id', '_id', type=int, default=None)
def html(_id):
    generate_html(all_notes, _id)


@click.command()
@click.option('--id', '-id', '_id', type=int, default=None)
def pdf(_id):
    generate_pdf(all_notes, _id)


@click.command()
@click.option('-set', '--set', '_set', type=(str, str), multiple=True)
def settings(_set):
    if _set:
        new_settings = {}
        for key, value in _set:
            if key not in SETTINGS.keys(): 
                print('"{}" is not a valid setting'.format(key))            
            elif key == 'note_types':
                print('The value for "note_types" cannot be changed at the moment')
            else:
                new_settings[str(key)] = str(value)

        update_settings(new_settings)
    else:
        print_settings()


cli.add_command(init)
cli.add_command(update)
cli.add_command(create)
cli.add_command(edit)
cli.add_command(notes)
cli.add_command(links)
cli.add_command(sequence)
cli.add_command(show)
cli.add_command(tags)
cli.add_command(show)
cli.add_command(html)
cli.add_command(pdf)
cli.add_command(settings)


if __name__ == '__main__':
    cli()
