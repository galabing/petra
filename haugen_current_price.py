#!/usr/local/bin/python3

""" Lists stock prices at the end of the month.
"""

import argparse
import logging
import utils
from os import path

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--price_sample_dir', required=True)
  parser.add_argument('--yyyy_mm', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  price_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    input_path = '%s/%s.csv' % (args.price_sample_dir, ticker.replace('^', '_'))
    if not path.isfile(input_path):
      logging.warning('Input file is missing: %s' % input_path)
      continue
    with open(input_path, 'r') as fp:
      lines = fp.read().splitlines()
    found = False
    for line in lines:
      if line.startswith(args.yyyy_mm):
        d, v, p = line.split(' ')
        price_map[ticker] = float(p)
        found = True
        break
    if not found:
      logging.warning('Could not find current price data for %s' % ticker)
  with open(args.output_path, 'w') as fp:
    for ticker in sorted(price_map.keys()):
      print('%s %.2f' % (ticker, price_map[ticker]), file=fp)

if __name__ == '__main__':
  main()

