# import the main window object (mw) from aqt
from anki.notes import Note
from aqt import mw
# import all of the Qt GUI library
from aqt.qt import *
# import the "show info" tool from utils.py
from aqt.utils import showInfo


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    cardCount = mw.col.cardCount()
    # show a message box
    showInfo("Card count: %d" % cardCount)


# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)


# def monkey_patch_editor() -> None:
#     import aqt.addcards
#     original_setupButtons = aqt.addcards.AddCards.setupButtons
#
#     def new_setupButtons(self: aqt.addcards.AddCards):
#         original_setupButtons(self)
#         bb = self.form.buttonBox
#
#         # fill_fields_button = QPushButton("Fill German fields")
#         # bb.addButton(fill_fields_button, QDialogButtonBox.ButtonRole.ActionRole)
#         self.editor.addButton(None, "Fill German Fields", lambda _: None)
#
#     aqt.addcards.AddCards.setupButtons = new_setupButtons
#
#     original_setupEditor = aqt.addcards.AddCards.setupEditor
#
#     def new_setupEditor(self: aqt.addcards.AddCards) -> None:
#         original_setupEditor(self)
#         # self.editor._links['fill_german_fields'] = lambda _: None
#
#     aqt.addcards.AddCards.setupEditor = new_setupEditor
#
#
# monkey_patch_editor()

from anki.hooks import addHook
from aqt import mw
from aqt.editor import Editor


def my_custom_function(editor: Editor):
    print("Button clicked!")
    # Your custom code here
    from pprint import pprint
    pprint(editor.__dict__)
    # pprint(editor.note.__dict__)
    note: Note = editor.note
    note['Word'] = 'foobar'
    editor.loadNote()

    #editor.web.eval()


def add_my_button(buttons, editor):
    btn = editor.addButton(
        icon=None,
        cmd="myButton",
        func=lambda s=editor: my_custom_function(s),
        tip="Click me!",
        label="My Button"
    )
    buttons.append(btn)
    return buttons


def on_setup_webview(editor):
    editor._links['myButton'] = my_custom_function


addHook("setupEditorButtons", add_my_button)
addHook("setupEditorWebView", on_setup_webview)
