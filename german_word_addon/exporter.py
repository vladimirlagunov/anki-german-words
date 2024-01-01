from PyQt6 import QtGui

import aqt
import shutil
from anki.notes import NoteId
from aqt import mw
from aqt.browser import Browser
from aqt.qt import *
from aqt.utils import showInfo
from german_word_addon.filler import get_universal_german_word_note_type
from typing import Sequence


def export_collection(note_ids: Sequence[NoteId], path: str, delete_old: bool) -> None:
    note_type = get_universal_german_word_note_type(mw)
    if delete_old:
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

    _export_note_type(note_type, path)

    count = 0
    for note_id in note_ids:
        note = mw.col.get_note(note_id)
        if note.note_type()['name'] == note_type['name']:
            file_path = note['Word'].strip().replace('/', '__').lower()
            file_path = os.path.join(
                path,
                file_path.removeprefix('sich').lstrip()[:1],
                file_path + '.txt',
            )

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            count += 1
            with open(file_path, 'w') as txt:
                for field, value in note.items():
                    if value:
                        txt.write(field)
                        txt.write('::: ')
                        txt.write(note[field])
                        txt.write('\n')

    showInfo(f"Written {count} cards.")


def _export_note_type(note_type, path):
    note_type_dir = os.path.join(path, "note_type")
    os.makedirs(note_type_dir, exist_ok=True)

    with open(os.path.join(note_type_dir, "fields.txt"), "w") as f:
        f.writelines(f['name'] + "\n" for f in note_type['flds'])

    with open(os.path.join(note_type_dir, "style.css"), "w") as f:
        f.write(note_type['css'])

    for template in note_type['tmpls']:
        template_dir = os.path.join(note_type_dir, f"template_{template['ord']:02d}")
        os.makedirs(template_dir, exist_ok=True)

        with open(os.path.join(template_dir, "name.txt"), "w") as f:
            f.write(template['name'])
            f.write('\n')

        with open(os.path.join(template_dir, "question_format.html"), "w") as f:
            f.write(template['qfmt'])

        with open(os.path.join(template_dir, "answer_format.html"), "w") as f:
            f.write(template['afmt'])


def export_cards(note_ids: Sequence[NoteId]) -> None:
    dialog = QDialog(aqt.mw)
    dialog.setWindowTitle("Export German Cards to a Directory")
    dialog.setModal(True)

    main_layout = QVBoxLayout()
    dialog.setLayout(main_layout)
    main_layout.addWidget(QLabel("Export cards to a directory:"))

    file_input_layout = QHBoxLayout()
    main_layout.addLayout(file_input_layout)

    path_edit = QLineEdit()
    file_input_layout.addWidget(path_edit)

    browse_button = QPushButton("Browse")
    file_input_layout.addWidget(browse_button)

    @browse_button.clicked.connect
    def _browse_clicked():
        file_name = QFileDialog.getExistingDirectory(dialog, "Choose a Directory")
        if file_name:
            path_edit.setText(file_name)

    delete_checkbox = QCheckBox("Delete old files")
    main_layout.addWidget(delete_checkbox)
    delete_checkbox.setChecked(True)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    main_layout.addWidget(button_box)
    button_box.button(QDialogButtonBox.StandardButton.Save).setAutoDefault(True)
    button_box.button(QDialogButtonBox.StandardButton.Save).setDefault(True)
    button_box.button(QDialogButtonBox.StandardButton.Cancel).setAutoDefault(False)
    button_box.button(QDialogButtonBox.StandardButton.Cancel).setDefault(False)

    @button_box.accepted.connect
    def _save():
        path = path_edit.text().strip()
        dialog.close()
        if path:
            export_collection(note_ids, path, delete_old=delete_checkbox.isChecked())

    @button_box.rejected.connect
    def _cancel():
        dialog.close()

    dialog.show()


def init_export_actions():
    action = QAction("Export cards in pretty format", mw)
    qconnect(action.triggered, export_cards)
    mw.form.menuTools.addAction(action)


def on_browser_setup_menus(browser: Browser):
    action = QtGui.QAction(parent=browser)
    action.setText("Export Universal German Cards")
    qconnect(action.triggered, lambda: export_cards(browser.selected_notes()))
    browser.form.menu_Notes.addAction(action)