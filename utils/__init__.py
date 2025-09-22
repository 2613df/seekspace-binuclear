__all__ = ['preprocess','pipeline','log','filter_noise']
__version__ = "0.0.3"
__author__ = "Xiaozhi"

from .log import *
import os
wt_log(__name__,"info",f"Log -> {os.getcwd()}")
wt_log(__name__,"info","Init modules success.")