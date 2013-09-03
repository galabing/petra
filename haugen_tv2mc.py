#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--trading_volumes_path', required=True)
  parser.add_argument('--prices_path', required=True)
  parser.add_argument('--outstanding_shares_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  tv_map = utils.read_map(args.trading_volumes_path)
  p_map = utils.read_map(args.prices_path)
  s_map = utils.read_map(args.outstanding_shares_path)
  tickers = tv_map.keys() & p_map.keys() & s_map.keys()

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(tickers):
      output = tv_map[ticker] / (p_map[ticker] * s_map[ticker])
      print('%s %f' % (ticker, output), file=fp)

if __name__ == '__main__':
  main()

