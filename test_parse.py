import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from backend.parser.ner import parse_resume
    result = parse_resume("This is a software engineer resume with Python and React.")
    print("Success:", result)
except Exception as e:
    import traceback
    traceback.print_exc()
