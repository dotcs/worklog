from typing import Optional
import shutil
import os


def get_pager() -> Optional[str]:
    # Windows comes pre-installed with the 'more' pager.
    # See https://superuser.com/a/426229
    # Unix distributions also have 'more' pre-installed.
    more_bin = shutil.which("more")
    less_bin = shutil.which("less")
    default_pager = more_bin
    if less_bin is not None:
        default_pager = less_bin
    pager = os.getenv("PAGER", default_pager)
    return pager
