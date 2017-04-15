import sys

PY2 = False
PY3 = True
if sys.version_info[0] < (3):
   PY3 = False
   PY2 = True

text_type = str
if PY2:
    text_type = unicode # noqa
   
