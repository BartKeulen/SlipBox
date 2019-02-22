import os
import pdb

import pypandoc as pd

from .sb_config import get_setting, get_sb_dir
from .sb_core import get_links_in, get_children

index_html_build = False 

def generate_html(notes, note=None):
    global index_html_build
    if not index_html_build:
        generate_overview(notes)
        index_html_build = True
        
    if note is None:
        for _note in notes:
            generate_html(notes, _note)
        return

    filters = ['pandoc-citeproc']
    pdoc_args = ['--mathjax',
                    '-s',
                    '--verbose',
                    '--metadata=reference-section-title:References',
                    '--variable=index:{}'.format(get_setting('index')),
                    '--template={}'.format(os.path.join(get_sb_dir(),
                                                        'template.html')),
                    '--bibliography={}'.format(os.path.join(
                        get_sb_dir(), 'bibliography.bib'))]

    # Add links and sequence
    links_in = get_links_in(notes, note)
    links_out = note.get_links_out()
    children = get_children(notes, note)
    parents = note.get_parents()

    if links_in:
        pdoc_args.append('--variable=links_in:{}'.format(list_to_html(links_in)))
    if links_out:
        pdoc_args.append('--variable=links_out:{}'.format(list_to_html(links_out)))
    if parents:
        pdoc_args.append('--variable=parents:{}'.format(list_to_html(parents)))
    if children:
        pdoc_args.append('--variable=children:{}'.format(list_to_html(children)))

    # Add panflute filters
    for root, dirs, files in os.walk(os.path.join(get_sb_dir(), 'filters')):
        for name in files:
            pdoc_args.append('--filter={}'.format(os.path.join(root, name)))

    # Generate html
    outputfile = os.path.join(os.path.join(
        get_sb_dir(), get_setting('html_path')), '{}.html'.format(note.id))
    pd.convert_file(source_file=note.get_fp(),
                    to='html5',
                    format='md',
                    outputfile=outputfile,
                    extra_args=pdoc_args,
                    filters=filters)
    print('Generated html for note: {}'.format(note))


def list_to_html(note_list):
    html_str = '<ul>\n'
    for note in note_list:
        html_str += '<li><a href="{}.html">[{}]</a> - {}</li>\n'.format(note.id, note.id, note.title)
    html_str += '</ul>'
    return html_str


def generate_overview(notes):
    md_str = '# Notes\n'
    for note in sorted(notes):
        md_str += '\n- [[{}]] - {}'.format(note.id, note.title)

    filters = ['pandoc-citeproc']
    pdoc_args = ['--mathjax',
                '-s',
                '--metadata=reference-section-title:References',
                '--variable=index:{}'.format(get_setting('index')),
                '--variable=pagetitle:{}'.format('Overview'),
                '--template={}'.format(os.path.join(get_sb_dir(), 'template.html')),
                '--bibliography={}'.format(os.path.join(get_sb_dir(),'bibliography.bib')), 
                # '--csl={}'.format(os.path.join(get_sb_dir(), 'ieee.csl')),
                '--filter={}'.format(os.path.join(get_sb_dir(), 'filters/wiki_links.py'))]
    outputfile = os.path.join(get_sb_dir(), get_setting('html_path'), 'overview.html')
    pd.convert_text(md_str,
                        to='html5',
                        format='md',
                        outputfile=outputfile,
                        extra_args=pdoc_args,
                        filters=filters)
    print('Generated html for page: overview')

def generate_pdf(notes, note=None):
    print('PDF generation is note implemented yet')
    exit()