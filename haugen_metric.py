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
  # Aggregate the last k quarters' data.
  parser.add_argument('--k', default='1')
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  k = int(args.k)
  assert k > 0

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
    # We require n - 1 >= k + 1:
    # n - 1: the number of quarters for which data is available
    # k: the number of quarters for which data is needed
    # We further need k + 1 quarters, at least for the dates, because we
    # want to ensure that the previous (k + 1)th quarter deed ends at a
    # proper date.  Otherwise the first quarter we use is not a valid span.
    if n - 1 < k + 1:
      logging.warning('Not enough quarters for aggregation:'
                      ' wanted at least %d, saw %d' % (k+1, n-1))
      continue
    indexes = None
    for j in range(len(items) - 1, 0, -1):
      # Sanity check of format validity.
      y, m = items[j].split('-')
      y, m = int(y), int(m)
      if items[j] <= args.yyyy_mm:
        # We found the most recent quarter.  Now push the most recent k
        # quarters in.  Bail if we have less than k left.
        if j >= k + 1:
          indexes = list(range(j-k+1, j+1))
        break
    if indexes is None:
      logging.warning('Not enough recent quarters for aggregation')
      continue
    logging.debug('Index is %s' % indexes)
    assert len(indexes) == k
    if distance(args.yyyy_mm, items[indexes[-1]]) > 6:
      logging.warning('The most recent quarter is not recent enough')
      continue
    is_quarterly = True
    for j in indexes:
      if distance(items[j], items[j-1]) != 3:
        is_quarterly = False
        break
    if not is_quarterly:
      logging.warning('Data is not quarterly')
      continue
    found = False
    for j in range(1, len(lines)):
      items = lines[j].split(',')
      assert len(items) == n
      if items[0] == args.metric:
        metric = 0.0
        for jj in indexes:
          if items[jj] != '':
            metric += float(items[jj])
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

