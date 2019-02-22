import os
import copy
import pdb
import subprocess

import datetime
import click
import click_completion

from .sb_config import *
from .sb_core import *
from .sb_build import *

note_ids, note_titles, all_notes = None, None, None
click_completion.init()


@click.group('note')
@click.option('--dir', '_dir', default=None, type=str)
@click.option('-d', '--debug', default=False, flag_value=True)
def cli(_dir, debug):
    global note_ids, note_titles, all_notes

    if debug:
        print('Debug mode is not implemented yet')

    if not _dir:
        _dir = find_sb_dir()
    set_sb_dir(_dir)
    load_settings(SETTINGS)
    all_notes, note_ids, note_titles = get_all_notes()


@click.command()
def init():
    init_sb_folder()


@click.command()
@click.argument('title')
@click.option('-e', '--edit', flag_value=True, default=False)
@click.option('-t', '--tag', default=None, multiple=True, type=str, help='tag for note, each tag has to be added separately')
@click.option('-p', '--parent', default=None, multiple=True, type=str, help='parent of note, each parent has to be added separately')
@click.option('-type', '--type', 'note_type', default=None, type=str, help='Note type')
@click.option('-bib', '--bibkey', default=None, type=str, help='Bibkey of reference')
@click.option('-c', '--content', default=None, type=str, help='Content of Note')
def create(title, edit, tag, parent, note_type, bibkey, content):
    global note_ids, note_titles, all_notes
    note_id = get_new_note_id(all_notes)
    tags = [str(t) for t in tag]
    parents = [str(p) for p in parent]
    note = Note.create(note_id, title, tags, parents, note_type, content, bibkey)
    all_notes, note_ids, note_titles = get_all_notes()
    if edit:
        subprocess.call(['editor', note.get_fp()])


@click.command()
@click.option('-id', '--id', 'note_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str, help='title for note')
@click.option('--update_time', flag_value=True, default=False)
def update(note_id, title, update_time):
    global note_ids, note_titles, all_notes
    if note_id or title:
        note = Note.load(note_id=note_id, title=title)
        if update_time:
            note.date = datetime.datetime.now()
        if note:
            note.save()
    else:
        if update_time:
            print("You can only update the time one note at a time.")
        for note in all_notes:
            note.save()
    all_notes, note_ids, note_titles = get_all_notes()


@click.command()
@click.option('-id', '--id', 'note_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str)
def edit(note_id, title):
    note = Note.load(note_id=note_id, title=title)
    if note:
        subprocess.call(['editor', note.get_fp()])


@click.command()
@click.option('-a', '--al', '_all', flag_value=True, default=False)
@click.option('-t', '--tag', multiple=True, default=None, type=str, help='tag for note, each tag has to be added separately')
@click.option('--type', '-type', 'note_type', default=None, type=click.Choice(SETTINGS['note_types']), multiple=True)
def notes(_all, tag, note_type):
    notes = all_notes
    
    if not _all:
        _notes = []
        if not note_type:
            note_type = (SETTINGS['default_view_type'], )

        for note in notes:
            if note.note_type in note_type:
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
        output_str += '{}\n'.format(note)

    print(output_str[:-1])


@click.command()
@click.option('-id', '--id', 'note_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str)
def links(note_id, title):
    note = Note.load(note_id=note_id, title=title)
    links_out = note.get_links_out()
    links_in = get_links_in(all_notes, note)

    output_str = 'Links in:\n'
    for link in links_in:
        output_str += '  {}\n'.format(link)
    output_str += '\nLinks out:\n'
    for link in links_out:
        output_str += '  {}\n'.format(link)
    print(output_str)

@click.command()
@click.option('-id', '--id', 'note_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str)
def sequence(note_id, title):
    note = Note.load(note_id=note_id, title=title)
    parents = note.get_parents()
    children = get_children(all_notes, note)

    output_str = 'Parents:\n'
    for parent in parents:
        output_str += '  {}\n'.format(parent)
    output_str += '\nChildren:\n'
    for child in children:
        output_str += '  {}\n'.format(child)
    print(output_str)


@click.command()
@click.option('-id', '--id', 'note_id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str)
def show(note_id, title):
    note = Note.load(note_id=note_id, title=title)
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
@click.option('--id', '-id', 'note_id', type=int, default=None)
@click.option('-f', '--file', 'filename', type=str, default=None)
@click.option('-format', '--format', default='html', type=click.Choice(['html', 'pdf']))
@click.option('--index', flag_value=True, default=False)
def build(note_id, filename, format, index):
    global note_ids, note_titles, all_notes

    if index:
        generate_overview(all_notes)
        return

    if format == 'html':
        generate = generate_html
    elif format == 'pdf':
        generate = generate_pdf
    else:
        print('{} not a valid output format, choose from ["html", "pdf"]')
        return

    if filename and os.path.isfile(filename):
        f_split = filename.split('/')
        set_sb_dir('/'.join(f_split[:-2]))
        all_notes, note_ids, note_titles = get_all_notes()
        note = Note.load(filename=filename)
        generate(all_notes, note)
    elif filename or note_id:
        note = Note.load(filename=filename, note_id=note_id)
        if note:
            generate(all_notes, note)
    else:
        generate(all_notes)


@click.command()
@click.option('--id', '-id', 'note_id', type=int, default=None)
@click.option('-f', '--file', 'filename', type=str, default=None)
def html(note_id, filename):
    if filename and os.path.isfile(filename):
        global note_ids, note_titles, all_notes
        f_split = filename.split('/')
        set_sb_dir('/'.join(f_split[:-2]))
        all_notes, note_ids, note_titles = get_all_notes()
        note = Note.load(filename=filename)
        subprocess.call(['x-www-browser', note.get_fp('html')])
        return
    elif note_id or filename:
        note = Note.load(note_id=note_id, filename=filename)
        if note:
            subprocess.call(['x-www-browser', note.get_fp('html')])
    else:
        print('No note found with id {} and/or filename {}'.format(note_id, filename))


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
cli.add_command(build)
cli.add_command(html)
cli.add_command(settings)

