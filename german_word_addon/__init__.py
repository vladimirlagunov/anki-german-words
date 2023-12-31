import sys

if "anki" in sys.modules:
    from .init_plugin import init_plugin

    init_plugin()
