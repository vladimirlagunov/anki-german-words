import os
from anki.hooks import addHook
from . import filler

if os.environ.get('ANKIDEV'):
    import importlib
    import time
    from threading import Thread

    def refresher():
        while True:
            importlib.reload(filler)
            time.sleep(2)

    t = Thread(target=refresher)
    t.daemon = True
    t.start()


addHook("setupEditorButtons", lambda *a, **kw: filler.add_my_button(*a, **kw))
addHook("setupEditorWebView", lambda *a, **kw: filler.on_setup_webview(*a, **kw))
