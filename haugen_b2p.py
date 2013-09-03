#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--total_assets_path', required=True)
  parser.add_argument('--intangible_assets_path', required=True)
  parser.add_argument('--total_liabilities_path', required=True)
  parser.add_argument('--prices_path', required=True)
  parser.add_argument('--outstanding_shares_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  ta_map = utils.read_map(args.total_assets_path)
  tl_map = utils.read_map(args.total_liabilities_path)
  p_map = utils.read_map(args.prices_path)
  s_map = utils.read_map(args.outstanding_shares_path)
  tickers = ta_map.keys() & tl_map.keys() & p_map.keys() & s_map.keys()

  # intangible assets are 0 by default
  ia_map = dict()
  for t in tickers:
    ia_map[t] = 0.0
  ia_part = utils.read_map(args.intangible_assets_path)
  for k, v in ia_part.items():
    ia_map[k] = v

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(tickers):
      output = ((ta_map[ticker] - ia_map[ticker] - tl_map[ticker])
                / s_map[ticker] / p_map[ticker])
      print('%s %f' % (ticker, output), file=fp)

if __name__ == '__main__':
  main()

