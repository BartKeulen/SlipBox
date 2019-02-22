import pdb
import os
import yaml


SETTINGS = {
    'attachments_path': 'attachments',
    'html_path': 'html',
    'notes_path': 'notes',
    'pdf_path': 'pdf',
    'index': 'index',
    'default_new_type': 'Inbox',
    'default_view_type': 'Archive',
    'note_types': ['Inbox', 'Archive', 'Reference'],
    'tikz_format': 'png'
}

SB_DIR = None


def find_sb_dir():
    cur_dir = os.getcwd()
    while not os.path.isfile(os.path.join(cur_dir, '.slipbox')):
        parent_dir = os.path.dirname(cur_dir)
        if parent_dir == cur_dir:
            global_dir = os.environ.get('SB_GLOBAL_DIR')
            if global_dir is not None and os.path.isfile(os.path.join(global_dir, '.slipbox')):
                return global_dir
            raise Exception("No valid slipbox configuration found in current directory or any parent directory and no global slipbox configuration found.")
        cur_dir = parent_dir
    return cur_dir


def get_sb_dir():
    if SB_DIR is None:
        print('No SlipBox found. Call from a valid SlipBox project folder or set global SlipBox directory.')
        exit()
    return SB_DIR


def set_sb_dir(fp):
    global SB_DIR
    SB_DIR = fp


def load_settings(settings=None):
    if not settings:
        settings = {}

    with open(os.path.join(SB_DIR, '.slipbox'), 'r') as stream:
        try:
            settings.update(yaml.load(stream))
        except yaml.YAMLError as exc:
            print(exc)
    
    return settings

def init_sb_folder():
    for key, value in SETTINGS.items():
        if 'path' in key:
            if value[0] != '/':
                value = os.path.join(SB_DIR, value)
            if not os.path.exists(value):
                os.makedirs(value)


def update_settings(new_settings):
    settings = load_settings()
    settings.update(new_settings)
    with open(os.path.join(SB_DIR, '.slipbox'), 'w') as stream:
        try:
            yaml.dump(settings, stream, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)
    init_sb_folder()


def print_settings():
    output_str = 'Settings:\n'
    for key, value in SETTINGS.items():
        output_str += '  {}: {}\n'.format(key, value)
    print(output_str[:-1])


def get_setting(key):
    if key in SETTINGS.keys():
        return SETTINGS[key]
    else:
        print('{} is not a valid settings entry.'.format(key))
