#!/usr/local/bin/python3

import argparse
import logging
import utils
from csv import reader
from os import path

def get_operating_cashflow(metric_map):
  return metric_map['|Net cash provided by operating activities']

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
  operating_cashflow = get_operating_cashflow(metric_map)
  with open(output_path, 'w') as fp:
    print(','.join(['date'] + dates), file=fp)
    print(','.join(['operating_cashflow'] + operating_cashflow), file=fp)

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

