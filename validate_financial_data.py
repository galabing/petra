#!/usr/local/bin/python3

""" Validates that downloaded financial reports contain expected metrics.
"""

import argparse
import logging
import utils
from os import path

IS_MAP = {
    'Weighted average shares outstanding': 'outstanding-shares',
    'Net income,': 'net-income',
    'Net income available to common shareholders,': 'net-income-common',
    'Earnings per share': 'eps',
    'Revenue,': 'revenue',
}
TYPE_MAP = {
    'is': IS_MAP,
}

def validate(input_path, metric_map):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  metrics = set()
  for line in lines:
    for prefix in metric_map.keys():
      if line.startswith(prefix):
        metrics.add(metric_map[prefix])
        break
  diff = set(metric_map.values()) - metrics
  assert len(diff) == 0, 'Non-empty diff: %s' % diff

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--report_type', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  rt = args.report_type
  assert rt in TYPE_MAP, (
      'report_type must be one of %s' % TYPE_MAP.keys())
  metric_map = TYPE_MAP[rt]

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    input_path = '%s/%s.csv' % (args.input_dir, ticker)
    if not path.isfile(input_path):
      logging.warning('Input file does not exist: %s' % input_path)
      continue
    validate(input_path, metric_map)

if __name__ == '__main__':
  main()

