import argparse
import os
import re
import shutil
from anki.collection import Collection, ExportAnkiPackageOptions
from aqt import ProfileManager
from german_word_addon.filler import universal_german_word_template_name, _fill_note_from_wiktionary
from tempfile import mkdtemp
from typing import Sequence, Tuple, TextIO


def handle_a1_cards():
    pm = ProfileManager(ProfileManager.get_created_base_folder(None))
    pm.setupMeta()
    pm.load(next(iter(pm.profiles())))

    col = Collection(pm.collectionPath())

    note_ids = col.find_notes('deck:"A1 tmp"')

    for note_id in note_ids:
        note = col.get_note(note_id)

        word = note['Word']

        import bs4
        word = bs4.BeautifulSoup(word, 'html.parser').get_text().strip()

        word = (
            word
            .strip()
            .split("\n", 1)[0]
            .removeprefix('der ')
            .removeprefix('die ')
            .removeprefix('das ')
            .rstrip()
        )
        word = re.sub('[-(,].*', '', word)

        note['Word'] = word
        print("Checking word:", word)

        _fill_note_from_wiktionary(note)

        col.update_note(note)

    col.save()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    generate_apkg_parser = subparsers.add_parser('generate-apkg')
    generate_apkg_parser.set_defaults(cmd='generate-apkg')
    generate_apkg_parser.add_argument("path")

    tmp_parser = subparsers.add_parser("tmp")
    tmp_parser.set_defaults(cmd='tmp')

    args = parser.parse_args()

    if args.cmd == 'tmp':
        handle_a1_cards()
        return

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

        col.media.add_file("_universal_german_cards.js")

        col.export_anki_package(
            out_path=os.path.join(args.path, 'export.apkg'),
            limit=None,
            options=ExportAnkiPackageOptions(
                with_scheduling=False,
                with_media=True,
            )
        )

        col.export_note_csv(
            out_path=os.path.join(args.path, 'export.csv'),
            limit=None,
            with_html=True,
            with_tags=True,
            with_guid=True,
            with_notetype=True,
            with_deck=False,
        )

        col.export_collection_package(
            out_path=os.path.join(args.path, 'export.colpkg'),
            include_media=True,
            legacy=False,
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
        for field_id, line in enumerate(f.readlines()):
            field = col.models.new_field(line.strip())
            field['ord'] = field_id
            col.models.add_field(note_type, field)

    with open(os.path.join(note_type_dir, "style.css")) as f:
        note_type['css'] = f.read(1024 * 1024)

    template_dirs = sorted(
        (dir_name for dir_name in os.listdir(note_type_dir) if re.match(r'^template_(\d+)$', dir_name)),
        key=lambda dir_name: int(re.match(r'^template_(\d+)$', dir_name).groups()[0]),
    )
    for template_id, dir_name in enumerate(template_dirs):
        with open(os.path.join(note_type_dir, dir_name, "name.txt")) as f:
            template = col.models.new_template(f.read(1024).strip())

        template['ord'] = template_id

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
