from anki.collection import Collection
from aqt import ProfileManager
from pprint import pprint
from random import sample

if __name__ == '__main__':
    pm = ProfileManager(ProfileManager.get_created_base_folder(None))
    pm.setupMeta()
    pm.load(next(iter(pm.profiles())))
    #pm.auth = pm.sync_auth()

    col = Collection(pm.collectionPath())
    note_ids = col.find_notes("flag:7")

    result = []
    for note_id in note_ids:
        note = col.get_note(note_id)
        result.append(dict(note.items()))
    pprint(sample(result, 30))