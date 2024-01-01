import os

if not os.environ.get('TOOL'):
    from .init_plugin import init_plugin

    init_plugin()
