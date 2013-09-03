#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--net_income_path', required=True)
  parser.add_argument('--total_equity_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  ni_map = utils.read_map(args.net_income_path)
  e_map = utils.read_map(args.total_equity_path)
  tickers = ni_map.keys() & e_map.keys()

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(tickers):
      output = ni_map[ticker] / e_map[ticker]
      print('%s %f' % (ticker, output), file=fp)

if __name__ == '__main__':
  main()

