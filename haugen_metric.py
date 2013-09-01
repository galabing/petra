#!/usr/local/bin/python3

""" Extracts certain metric from certain date.
"""

import argparse
import logging
import utils
from os import path

def distance(ym1, ym2):
  y1, m1 = ym1.split('-')
  y2, m2 = ym2.split('-')
  y1, m1 = int(y1), int(m1)
  y2, m2 = int(y2), int(m2)
  return (y1 - y2) * 12 + m1 - m2

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--metric', required=True)
  parser.add_argument('--yyyy_mm', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  metric_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    input_path = '%s/%s.csv' % (args.input_dir, ticker.replace('^', '_'))
    if not path.isfile(input_path):
      logging.warning('Input file is missing: %s' % input_path)
      continue

    with open(input_path, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    items = lines[0].split(',')
    n = len(items)
    assert n > 0
    assert items[0] == 'date'
    index = -1
    for j in range(len(items) - 1, 0, -1):
      # Sanity check of format validity.
      y, m = items[j].split('-')
      y, m = int(y), int(m)
      if items[j] <= args.yyyy_mm:
        index = j
        break
    logging.debug('Using %s for %s' % (items[index], ticker))
    if index <= 0 or distance(args.yyyy_mm, items[index]) > 6:
      logging.warning('Could not find any recent date for %s' % ticker)
      continue
    found = False
    for j in range(1, len(lines)):
      items = lines[j].split(',')
      assert len(items) == n
      if items[0] == args.metric:
        metric = items[index]
        if metric == '':
          break
        metric_map[ticker] = float(metric)
        found = True
        break
    if not found:
      logging.warning('Could not find %s for %s' % (args.metric, ticker))
  with open(args.output_path, 'w') as fp:
    for ticker in sorted(metric_map.keys()):
      print('%s %f' % (ticker, metric_map[ticker]), file=fp)

if __name__ == '__main__':
  main()

