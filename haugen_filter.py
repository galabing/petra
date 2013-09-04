#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

MIN_PRICE = 5.0
MIN_MC = 300.0 * 1000 * 1000

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--scores_path', required=True)
  parser.add_argument('--prices_path', required=True)
  parser.add_argument('--mc_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  s_map = utils.read_map(args.scores_path)
  p_map = utils.read_map(args.prices_path)
  mc_map = utils.read_map(args.mc_path)
  tickers = s_map.keys() & p_map.keys() & mc_map.keys()

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(tickers):
      if p_map[ticker] < MIN_PRICE: continue
      if mc_map[ticker] < MIN_MC: continue
      print('%s %f' % (ticker, s_map[ticker]), file=fp)

if __name__ == '__main__':
  main()

