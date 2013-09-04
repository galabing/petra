#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

# From table 1 of Haugen's paper.
ER1 = ((-.97) + (-.72))/2
ER12 = (.52 + .52) / 2
TV2MC = ((-.35) + (-.2)) / 2
ER2 = ((-.2) + (-.11)) / 2
E2P = (.27 + .26) / 2
ROE = (.24 + .13) / 2
B2P = (.35 + .39) / 2
ER6 = (.24 + .19) / 2
CF2P = (.13 + .26) / 2

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--er1_path', required=True)
  parser.add_argument('--er12_path', required=True)
  parser.add_argument('--tv2mc_path', required=True)
  parser.add_argument('--er2_path', required=True)
  parser.add_argument('--e2p_path', required=True)
  parser.add_argument('--roe_path', required=True)
  parser.add_argument('--b2p_path', required=True)
  parser.add_argument('--er6_path', required=True)
  parser.add_argument('--cf2p_path', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  er1_map = utils.read_map(args.er1_path)
  er12_map = utils.read_map(args.er12_path)
  tv2mc_map = utils.read_map(args.tv2mc_path)
  er2_map = utils.read_map(args.er2_path)
  e2p_map = utils.read_map(args.e2p_path)
  roe_map = utils.read_map(args.roe_path)
  b2p_map = utils.read_map(args.b2p_path)
  er6_map = utils.read_map(args.er6_path)
  cf2p_map = utils.read_map(args.cf2p_path)
  tickers = (er1_map.keys() & er12_map.keys() & tv2mc_map.keys()
             & er2_map.keys() & e2p_map.keys() & roe_map.keys()
             & b2p_map.keys() & er6_map.keys() & cf2p_map.keys())
  logging.info('%d tickers' % len(tickers))
  logging.info('total weight: %f' %
      (ER1 + ER12 + TV2MC + ER2 + E2P + ROE + B2P + ER6 + CF2P))

  with open(args.output_path, 'w') as fp:
    for t in sorted(tickers):
      score = (er1_map[t] * ER1
               + er12_map[t] * ER12
               + tv2mc_map[t] * TV2MC
               + er2_map[t] * ER2
               + e2p_map[t] * E2P
               + roe_map[t] * ROE
               + b2p_map[t] * B2P
               + er6_map[t] * ER6
               + cf2p_map[t] * CF2P) / 100  # accounting for %
      print('%s %f' % (t, score), file=fp)

if __name__ == '__main__':
  main()

