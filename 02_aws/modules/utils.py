"""
    Utils
"""

from pathlib import Path
from datetime import datetime as dtt

# ---------------------------------------
def get_filename(filepath):
    """
        return aaa

        parameter
        ---------
        1. filepath: xxx/xxx/aaa.bbb
    """
    file_path = Path(filepath)
    file_name_no_extension = file_path.stem
    return file_name_no_extension

def get_date():
    """
        return yymmdd
    """

    tmp_now = dtt.now()
    return f'{tmp_now.year}{tmp_now.month}{tmp_now.day}'