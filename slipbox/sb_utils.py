

def id_title_from_filename(filename):
    note_id, title = filename.split('.')[0].split(' - ')
    return int(note_id), title