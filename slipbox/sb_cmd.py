import os
import subprocess

import click

from .sb_config import SB_DIR, SETTINGS, init_sb
from .sb_core import Note, get_notes_with_tag, get_tags, get_notes_with_project, get_projects, get_all_notes, generate_html, generate_pdf

NOTES_DIR = os.path.join(SB_DIR, SETTINGS['notes_path'])


@click.group('note')
def cli():
    pass


@click.command()
def init():
    init_sb()


@click.command()
@click.argument('title')
@click.option('-t', '--tag', default=None, multiple=True, type=str, help='tag for note, each tag has to be added separately')
@click.option('-pr', '--project', default=None, type=str, help='project')
@click.option('-p', '--parent', default=None, multiple=True, type=str, help='parent of note, each parent has to be added separately')
@click.option('-type', '--type', default=None, type=str, help='Note type')
@click.option('-bib', '--bibkey', default=None, type=str, help='Bibkey of reference')
@click.option('-c', '--content', default=None, type=str, help='Content of Note')
def create(title, tag, project, parent, type, content, bibkey):
    tags = [str(t) for t in tag]
    parents = [str(p) for p in parent]
    Note.create(title, tags, project, parents, type, content, bibkey)


@click.command()
@click.argument('id', type=int)
@click.option('-title', '--title', default=None, type=str, help='title for note')
@click.option('-t', '--tag', default=None, multiple=True, type=str, help='tag for note, each tag has to be added separately')
@click.option('-pr', '--project', default=None, type=str, help='project')
@click.option('-p', '--parent', default=None, multiple=True, type=str, help='parent of note, each parent has to be added separately')
@click.option('-type', '--type', default=None, type=str, help='Note type')
@click.option('-bib', '--bibkey', default=None, type=str, help='Bibkey of reference')
@click.option('-c', '--content', default=None, type=str, help='Content of Note')
def update(id, title, tag, project, parent, type, content, bibkey):
    note = Note.load(id)
    note.save()


@click.command()
@click.option('-id', '--id', default=None, type=int)
@click.option('-title', '--title', default=None, type=str)
def edit(id, title):
    note = Note.load(id, title)
    if note:
        subprocess.call(['editor', note.get_fp()])


@click.command()
@click.option('-pr', '--project', default=None, type=str, help='project')
@click.option('-t', '--tag', multiple=True, default=None, type=str, help='tag for note, each tag has to be added separately')
@click.option('--type', '-type', default=None, type=str)
def notes(project, tag, type):
    all_notes = get_all_notes()
    notes = []
    if type:
        for note in all_notes:
            if type == note.note_type:
                notes.append(note)
        all_notes = notes

    if project:
        for note in all_notes:
            if project == note.project:
                notes.append(note)
        all_notes = notes
            
    tags = [str(t) for t in tag]
    notes = []
    if tags:
        for note in all_notes:
            for _tag in tags:
                if _tag in note.tags:
                    notes.append(note)
        all_notes = notes
    
    # Sort notes on id
    notes = sorted(all_notes)

    # output_str = 'Notes:\n'
    output_str = ''
    for note in notes:
        output_str += '{}\n'.format(repr(note))

    print(output_str[:-1])


@click.command()
@click.argument('id', type=int)
def links(id):
    note = Note.load(id)
    note.print_links()


@click.command()
@click.argument('id', type=int)
def sequence(id):
    note = Note.load(id)
    note.print_sequence()


@click.command()
@click.argument('id', type=int)
def show(id):
    note = Note.load(id)
    note.show()


@click.command()
def tags():
    tags = get_tags()
    # output_str = 'Tags:\n'
    output_str = ''
    for tag in tags:
        output_str += '{}\n'.format(tag)
    print(output_str[:-1])


@click.command()
def projects():
    projects = get_projects()
    # output_str = 'Projects:\n'
    output_str = ''
    for project in projects:
        output_str += '{}\n'.format(project)
    print(output_str[:-1])


@click.command()
@click.option('--id', '-id', type=int, default=None)
def html(id):
    generate_html(id)


@click.command()
@click.option('--id', '-id', type=int, default=None)
def pdf(id):
    generate_pdf(id)

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
cli.add_command(projects)
cli.add_command(html)
cli.add_command(pdf)


if __name__ == '__main__':
    cli()
