from typing import List, Iterable, Tuple, Dict, Optional, Union
from pandas import DataFrame, Series  # type: ignore
import logging
import sys
import argparse
import os
from functools import reduce
from datetime import datetime, date, timezone, timedelta, tzinfo
import shutil
from math import floor
import numpy as np

import worklog.constants as wc

