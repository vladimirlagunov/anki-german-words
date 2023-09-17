from anki.models import NotetypeDict
from anki.notes import Note
from aqt.editor import Editor
from aqt.utils import showWarning


def fill_german_word_fields(editor: Editor):
    from pprint import pprint
    pprint(editor.__dict__)
    # pprint(editor.note.__dict__)

    expected_note_type: NotetypeDict
    template_name = 'Universal German word template'
    if (expected_note_type := editor.mw.col.models.by_name(template_name)) is None:
        showWarning(f'There must be a note template called `{template_name}`. It is used for generating cards.')
        return

    note: Note = editor.note
    if note.note_type != expected_note_type:
        showWarning(f'The note type must be `{template_name}`.')

    note['Word'] = 'foobar'
    editor.loadNote()


def add_my_button(buttons, editor):
    btn = editor.addButton(
        icon=None,
        cmd="myButton",
        func=lambda s=editor: fill_german_word_fields(s),
        label="Fill German word fields"
    )
    buttons.append(btn)
    return buttons


def on_setup_webview(editor):
    editor._links['myButton'] = fill_german_word_fields
