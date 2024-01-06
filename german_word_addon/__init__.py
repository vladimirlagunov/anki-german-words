import sys

import os

if not os.environ.get('TOOL') and 'pytest' not in sys.modules:
    from .init_plugin import init_plugin

    init_plugin()
