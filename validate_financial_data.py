#!/usr/local/bin/python3

""" Validates that downloaded financial reports contain expected metrics.
"""

import argparse
import logging
import utils
from csv import reader
from os import path

# Tickers here are skipped for validation.
SKIPPED_TICKERS = {
}

# The logic is the following:
#
# For each report type, there are four maps:
# - req_map: Mapping keys to metrics.  Notice that multiple keys can lead
#   to the same metric, in which case one match is sufficient.
# - opt_map: Same as req_map, but the metrics are not required.
# - add_map: Additional mapping from metrics to possible combination of keys.
#   This is used when a metric corresponds to more than one lines in the csv
#   flie, and all the lines in one combination must be present in order to
#   compute the metric.  On ther other hand, only one combination is needed for
#   computing the metric.
# - skip_map: Mapping metrics to tickers that are known not to have this
#   metric.
#
# During validation, each csv file must fulfill all the metrics in the req_map,
# unless certain metrics are in the skip_map.  A first pass through the file
# will identify all the metrics computatable from a single line, and a second
# pass will be carried out, which examines multiple lines against add_map, if
# certain metrics are still missing.  The opt_map is for informational purposes
# (ie, it's nice to know how many tickers have optional metrics).
#
# Each key consists of <header>|<name>.  In many cases the header is empty
# string.

IS_REQ = {
    'Weighted average shares outstanding|Basic': 'outstanding-shares',
    '|Net income': 'net-income',
    '|Net income available to common shareholders': 'net-income-common',
    'Earnings per share|Basic': 'eps',
    '|Revenue': 'revenue',
    '|Total net revenue': 'revenue',
    '|Total revenues': 'revenue',
    '|Total interest and dividend income': 'revenue',
}
IS_OPT = {
    '|Preferred dividend': 'preferred-dividend',
}
IS_ADD = {
    'revenue': {
        ('|Total interest income',
         '|Total interest expense',
         '|Total noninterest revenue'),
    },
}
# TODO: Many of these below seem to use a different template for reporting,
# and the metrics are probably computatable in some way that I don't know.
IS_SKIP = {
    'revenue': {
        'CIE',
        'CIM',
        'CLVS',
        'CNDO',
        'EVR',
        'GHL',
        'GMO',
        'HNR',
        'IMUC',
        'ITG',
        'LORL',
        'MDW',
        'MITT',
        'MKTX',
        'MTGE',
        'ONTY',
        'PRKR',
        'SFE',
        'SGYP',
        'SNTA',
        'TAHO',
        'URZ',
        'VGZ',
        'VSTM',
        'VTUS',
    },
    'outstanding-shares': {
        'CSWC',
        'GLNG',
        'NWSA',
        'SVVC',
    },
    'eps': {
        'NWSA',
    },
}

BS_REQ = {
    '|Total assets': 'total-assets',
    '|Total liabilities': 'total-liabilities',
    "|Total stockholders' equity": 'total-equity',
    "|Total Stockholders' equity": 'total-equity',
}
BS_OPT = {
    '|Intangible assets': 'intangible-assets',
}
BS_ADD = {
    'total-liabilities': {
        ("|Total stockholders' equity",
         "|Total liabilities and stockholders' equity"),
    },
}
BS_SKIP = {
}

CF_REQ = {
    'Free Cash Flow|Operating cash flow': 'operating-cashflow',
    '|Net cash provided by operating activities': 'operating-cashflow',
}
CF_OPT = {
}
CF_ADD = {
}
CF_SKIP = {
}

TYPE_MAP = {
    'is': (IS_REQ, IS_OPT, IS_ADD, IS_SKIP),
    'bs': (BS_REQ, BS_OPT, BS_ADD, BS_SKIP),
    'cf': (CF_REQ, CF_OPT, CF_ADD, CF_SKIP),
}

def distance(ym1, ym2):
  y1, m1 = ym1.split('-')
  y2, m2 = ym2.split('-')
  y1, m1 = int(y1), int(m1)
  y2, m2 = int(y2), int(m2)
  return (y1 - y2) * 12 + m1 - m2

def find_additional(lines, combinations):
  header = ''
  keys = set()
  for items in reader(lines, delimiter=','):
    assert len(items) > 0
    if len(items) == 1:
      header = items[0]
      continue
    keys.add('%s|%s' % (header, items[0]))
    header = ''
  #logging.debug(keys)
  for c in combinations:
    #logging.debug(set(c))
    if set(c) <= keys:
      return True
  return False

# Returns: (keys, has_opt, is_quarterly).
def validate(input_path, ticker, req_map, opt_map, add_map, skip_map):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  # This is necessary for csv reader to work properly.
  for i in range(len(lines)):
    lines[i] = lines[i].replace('\ufeff"', '"')
  ttm = 0
  header = ''
  keys = set()
  metrics = set()
  is_quarterly = True
  for items in reader(lines, delimiter=','):
    assert len(items) > 0
    if len(items) == 1:
      header = items[0]
      continue
    if (items[0].startswith('Fiscal year ends in ')
        and items[-1] == 'TTM'):
      ttm = 1
      for j in range(1, len(items)-ttm-1):
        #assert distance(items[j+1], items[j]) == 3
        if distance(items[j+1], items[j]) != 3:
          is_quarterly = False
    assert len(items) == 6 + ttm, items

    key = '%s|%s' % (header, items[0])
    keys.add(key)
    hit = False
    if key in req_map:
      metrics.add(req_map[key])
      hit = True
    if key in opt_map:
      metrics.add(opt_map[key])
      hit = True
    if hit:
      for j in range(1, len(items)):
        try:
          v = float(items[j])
        except ValueError:
          # There are cases of missing values.
          #assert False, items
          pass
    header = ''
  diff = set(req_map.values()) - metrics
  final_diff = set()
  for d in diff:
    if d in skip_map and ticker in skip_map[d]:
      continue
    if d not in add_map:
      final_diff.add(d)
    elif not find_additional(lines, add_map[d]):
      final_diff.add(d)
  assert len(final_diff) == 0, 'Non-empty diff: %s' % final_diff
  return keys, len((metrics & set(opt_map.values()))) > 0, is_quarterly

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--from_ticker', default='')
  parser.add_argument('--report_type', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  rt = args.report_type
  assert rt in TYPE_MAP, (
      'report_type must be one of %s' % TYPE_MAP.keys())
  (req_map, opt_map, add_map, skip_map) = TYPE_MAP[rt]

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  total, opts, quarterly = 0, 0, 0
  common_keys = None
  for i in range(len(tickers)):
    ticker = tickers[i]
    if ticker < args.from_ticker or ticker in SKIPPED_TICKERS:
      logging.info('%d/%d: skipped %s' % (i+1, len(tickers), ticker))
      continue
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    input_path = '%s/%s.csv' % (args.input_dir, ticker)
    if not path.isfile(input_path):
      logging.warning('Input file does not exist: %s' % input_path)
      continue
    keys, has_opt, is_quarterly = validate(
        input_path, ticker, req_map, opt_map, add_map, skip_map)
    if common_keys is None:
      common_keys = keys
    else:
      common_keys &= keys
    if has_opt:
      opts += 1
    if is_quarterly:
      quarterly += 1
    total += 1
  logging.info('%d out of %d have optional metrics' % (opts, total))
  logging.info('%d out of %d are consecutive quarters' % (quarterly, total))
  logging.info('Common keys: %s' % common_keys)

if __name__ == '__main__':
  main()

