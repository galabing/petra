#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--operating_cashflow_path', required=True)
  parser.add_argument('--preferred_dividend_path', required=True)
  parser.add_argument('--prices_path', required=True)
  parser.add_argument('--outstanding_shares_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  cf_map = utils.read_map(args.operating_cashflow_path)
  p_map = utils.read_map(args.prices_path)
  s_map = utils.read_map(args.outstanding_shares_path)
  tickers = cf_map.keys() & p_map.keys() & s_map.keys()

  # preferred dividend is default to 0
  pd_map = dict()
  for t in tickers:
    pd_map[t] = 0.0
  pd_part = utils.read_map(args.preferred_dividend_path)
  for k, v in pd_part.items():
    pd_map[k] = v

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(tickers):
      output = ((cf_map[ticker] - pd_map[ticker])
                / s_map[ticker] / p_map[ticker])
      print('%s %f' % (ticker, output), file=fp)

if __name__ == '__main__':
  main()

