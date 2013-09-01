#!/usr/local/bin/python3

import argparse
import logging
import utils
from csv import reader
from os import path

# These tickers have known missing metrics detected during validation.
SKIPPED_TICKERS = {
    'CIE',
    'CIM',
    'CLVS',
    'CNDO',
    'CSWC',
    'EVR',
    'GHL',
    'GLNG',
    'GMO',
    'HNR',
    'IMUC',
    'ITG',
    'LORL',
    'MDW',
    'MITT',
    'MKTX',
    'MTGE',
    'NWSA',
    'ONTY',
    'PRKR',
    'SFE',
    'SGYP',
    'SNTA',
    'SVVC',
    'TAHO',
    'URZ',
    'VGZ',
    'VSTM',
    'VTUS',
}

REVENUE_KEYS = {
    '|Revenue',
    '|Total net revenue',
    '|Total revenues',
    '|Total interest and dividend income'
}

def get_revenue(metric_map):
  for key in REVENUE_KEYS:
    if key in metric_map:
      return metric_map[key]
  assert '|Total interest income' in metric_map
  assert '|Total interest expense' in metric_map
  assert '|Total noninterest revenue' in metric_map
  iincome = metric_map['|Total interest income']
  iexp = metric_map['|Total interest expense']
  nincome = metric_map['|Total noninterest revenue']
  assert len(iincome) == len(nincome) and len(iincome) == len(iexp)
  revenue = []
  for j in range(len(iincome)):
    i, e, n = 0.0, 0.0, 0.0
    if iincome[j] != '': i = float(iincome[j])
    if iexp[j] != '': e = float(iexp[j])
    if nincome[j] != '': n = float(nincome[j])
    revenue.append(i-e+n)
  return [str(r) for r in revenue]

def get_outstanding_shares(metric_map):
  return metric_map['Weighted average shares outstanding|Basic']

def get_net_income(metric_map):
  return metric_map['|Net income']

def get_net_income_common(metric_map):
  return metric_map['|Net income available to common shareholders']

def get_eps(metric_map):
  return metric_map['Earnings per share|Basic']

def get_preferred_dividend(metric_map):
  if '|Preferred dividend' not in metric_map:
    return None
  return metric_map['|Preferred dividend']

def parse(input_path, output_path):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  # This is necessary for csv reader to work properly.
  for i in range(len(lines)):
    lines[i] = lines[i].replace('\ufeff', '')
  ttm = 0
  header = ''
  metric_map = dict()
  dates = None
  for items in reader(lines, delimiter=','):
    assert len(items) > 0
    if len(items) == 1:
      header = items[0]
      continue
    if items[0].startswith('Fiscal year ends in '):
      if items[-1] == 'TTM': ttm = 1
      dates = items[1:len(items)-ttm]
    assert len(items) == 6 + ttm, items
    key = '%s|%s' % (header, items[0])
    metrics = items[1:len(items)-ttm]
    metric_map[key] = metrics
    header = ''
  assert dates is not None
  revenue = get_revenue(metric_map)
  outstanding_shares = get_outstanding_shares(metric_map)
  net_income = get_net_income(metric_map)
  net_income_common = get_net_income_common(metric_map)
  eps = get_eps(metric_map)
  preferred_dividend = get_preferred_dividend(metric_map)
  with open(output_path, 'w') as fp:
    print(','.join(['date'] + dates), file=fp)
    print(','.join(['revenue'] + revenue), file=fp)
    print(','.join(['outstanding_shares'] + outstanding_shares), file=fp)
    print(','.join(['net_income'] + net_income), file=fp)
    print(','.join(['net_income_common'] + net_income_common), file=fp)
    print(','.join(['eps'] + eps), file=fp)
    if preferred_dividend is not None:
      print(','.join(['preferred_dividend'] + preferred_dividend), file=fp)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  for i in range(len(tickers)):
    ticker = tickers[i]
    if ticker in SKIPPED_TICKERS:
      logging.warning('%d/%d: skipped %s' % (i+1, len(tickers), ticker))
      continue
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    input_path = '%s/%s.csv' % (args.input_dir, ticker)
    output_path = '%s/%s.csv' % (args.output_dir, ticker)
    if not path.isfile(input_path):
      logging.warning('Input file does not exist: %s' % input_path)
      continue
    if path.isfile(output_path) and not args.overwrite:
      logging.warning('Output file exists and not overwritable: %s'
          % output_path)
      continue
    parse(input_path, output_path)

if __name__ == '__main__':
  main()

