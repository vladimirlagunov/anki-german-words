import argparse
import os
import re
import shutil
from anki.collection import Collection
from aqt import ProfileManager
from german_word_addon.filler import universal_german_word_template_name
from tempfile import mkdtemp
from typing import Sequence, Tuple, TextIO


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    generate_apkg_parser = subparsers.add_parser('generate-apkg')
    generate_apkg_parser.add_argument("path")
    args = parser.parse_args()
    base_folder = mkdtemp()
    try:
        pm = ProfileManager(ProfileManager.get_created_base_folder(base_folder))
        pm.setupMeta()
        pm.create("export-profile")
        pm.load(next(iter(pm.profiles())))

        col = Collection(pm.collectionPath())

        deck = col.decks.get(
            col.decks.add_normal_deck_with_name("German Words").id
        )

        note_type_dir = os.path.join(args.path, "note_type")
        if not os.path.isdir(note_type_dir):
            raise Exception(f"No such directory: {note_type_dir}")

        note_type = _import_note_type(col, note_type_dir)

        _import_notes(col, deck, note_type, args.path)

        col.export_anki_package(
            out_path=os.path.join(args.path, 'export.apkg'),
            limit=None,
            with_scheduling=False,
            with_media=True,
            legacy_support=False,
        )
    finally:
        try:
            shutil.rmtree(base_folder)
        except:
            pass


def _import_notes(col, deck, note_type, path):
    field_names = [f['name'] for f in note_type['flds']]

    count = 0
    for dir in os.listdir(path):
        if dir != "note_type" and os.path.isdir(os.path.join(path, dir)):
            for fname in os.listdir(os.path.join(path, dir)):
                count += 1
                with open(os.path.join(path, dir, fname)) as f:
                    note_data_dict = dict(_read_note_data(f))
                    note = col.new_note(note_type)
                    note.guid = note_data_dict.pop('guid')
                    note.set_tags_from_str(note_data_dict.pop('Tags', ''))
                    note.fields = [
                        note_data_dict.get(field, '')
                        for field in field_names
                    ]
                    col.add_note(note, deck['id'])
                    col.after_note_updates([note.id], mark_modified=True)
                    col.update_cards(note.cards())
                    col.update_note(note)
    print(f"Read {count} notes")


def _import_note_type(col, note_type_dir):
    # note_type = col.models.new_template(universal_german_word_template_name)
    note_type = col.models.new(universal_german_word_template_name)

    with open(os.path.join(note_type_dir, "fields.txt")) as f:
        for line in f.readlines():
            col.models.add_field(note_type, col.models.new_field(line.strip()))

    with open(os.path.join(note_type_dir, "style.css")) as f:
        note_type['css'] = f.read(1024 * 1024)

    template_dirs = sorted(
        (dir_name for dir_name in os.listdir(note_type_dir) if re.match(r'^template_(\d+)$', dir_name)),
        key=lambda dir_name: int(re.match(r'^template_(\d+)$', dir_name).groups()[0]),
    )
    for dir_name in template_dirs:
        with open(os.path.join(note_type_dir, dir_name, "name.txt")) as f:
            template = col.models.new_template(f.read(1024).strip())

        with open(os.path.join(note_type_dir, dir_name, "question_format.html")) as f:
            template['qfmt'] = f.read(1024 * 1024)

        with open(os.path.join(note_type_dir, dir_name, "answer_format.html")) as f:
            template['afmt'] = f.read(1024 * 1024)

        col.models.add_template(note_type, template)

    col.models.save(note_type)

    return note_type


def _read_note_data(f: TextIO) -> Sequence[Tuple[str, str]]:
    key = ''
    value = ''
    for line in f.readlines():
        if m := re.match('^(.+?):::(.*)$', line):
            if key:
                yield key, value.rstrip()
            key, value = m.groups()
            value = value.lstrip()
        else:
            value += line
    if key:
        yield key, value
