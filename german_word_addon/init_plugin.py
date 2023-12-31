import os
from anki.hooks import addHook
from . import exporter
from . import filler


def init_plugin():
    addHook("setupEditorButtons", lambda *a, **kw: filler.add_my_buttons(*a, **kw))
    addHook("setupEditorWebView", lambda *a, **kw: filler.on_setup_webview(*a, **kw))
    addHook("browser.setupMenus", lambda *a, **kw: filler.on_browser_setup_menus(*a, **kw))
    addHook("browser.setupMenus", lambda *a, **kw: exporter.on_browser_setup_menus(*a, **kw))

    exporter.init_export_actions()

    if os.environ.get('ANKIDEV'):
        _init_refresher()


def _init_refresher():
    import importlib
    import time
    from threading import Thread
    from . import converter

    def refresher():
        while True:
            for lib in [filler, converter, exporter]:
                importlib.reload(lib)
            time.sleep(2)

    t = Thread(target=refresher)
    t.daemon = True
    t.start()
