#!/usr/local/bin/python3

""" Utilities shared by other scripts.
"""

import logging
from os import environ
from time import tzset

def setup_logging(verbose):
  environ['TZ'] = 'US/Pacific'
  tzset()
  level = logging.INFO
  if verbose:
    level = logging.DEBUG
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)

def read_map(filename):
  with open(filename, 'r') as fp:
    lines = fp.read().splitlines()
  m = dict()
  for line in lines:
    k, v = line.split(' ')
    m[k] = float(v)
  return m

