from aqt.profiles import ProfileManager
import os
_addon_folder = os.path.dirname(__file__)
ProfileManager.addonFolder = lambda _: _addon_folder

exec(open("anki/tools/run.py").read())