import pdb
import os
import yaml


def get_sb_dir():
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

SB_DIR = get_sb_dir()

def get_settings():
    with open(os.path.join(SB_DIR, '.slipbox'), 'r') as stream:
        try:
            settings = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return settings

SETTINGS = get_settings()

def init_sb():
    for key, value in SETTINGS.items():
        if 'path' in key:
            if value[0] != '/':
                value = os.path.join(SB_DIR, value)
            if not os.path.exists(value):
                os.makedirs(value)


def update_settings(new_settings):
    global SETTINGS
    SETTINGS.update(new_settings)
    with open(os.path.join(SB_DIR, '.slipbox'), 'w') as stream:
        try:
            yaml.dump(SETTINGS, stream, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)
    init_sb()

