#!/usr/local/bin/python3

""" Measures error of predicted returns.
"""

import argparse
import logging
import utils
from os import path

K = 10   # deciles

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--current_prices_path', required=True)
  parser.add_argument('--future_prices_path', required=True)
  parser.add_argument('--scores_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  cp_map = utils.read_map(args.current_prices_path)
  fp_map = utils.read_map(args.future_prices_path)
  s_map = utils.read_map(args.scores_path)
  tickers = cp_map.keys() & fp_map.keys() & s_map.keys()

  logging.info('%d tickers in this test' % len(tickers))
  scores = s_map.values()
  maxs, mins, means = max(scores), min(scores), sum(scores)/len(scores)
  logging.info('max score = %f, min score = %f, mean score = %f' %
      (maxs, mins, means))

  r_map = dict()
  for t in tickers:
    r_map[t] = (fp_map[t] - cp_map[t]) / (cp_map[t] + 0.01)  # avoid div-by-0

  ups, rups, corrects = 0, 0, 0
  for t in tickers:
    if (s_map[t] > 0) == (r_map[t] > 0):
      corrects += 1
    if s_map[t] > 0:
      ups += 1
    if r_map[t] > 0:
      rups += 1
  logging.info('%d of %d are predicted to go up' % (ups, len(tickers)))
  logging.info('%d of %d did go up' % (rups, len(tickers)))
  logging.info('%d of %d correct signs (%.2f%%)'
      % (corrects, len(tickers), 100.0 * corrects / len(tickers)))

  rs = [(t, s) for t, s in s_map.items()]
  rs.sort(key=lambda x: x[1])
  bucket_size = int(len(tickers) / K)
  for i in range(K):
    f = i * bucket_size
    t = f + bucket_size
    if i == K - 1: t = len(tickers)

    meanr, count = 0.0, 0
    for j in range(f, t):
      r = r_map[rs[j][0]]
      meanr += r
      count += 1
    meanr /= count
    logging.info('decile %d: %d stocks, mean return = %.2f%%'
        % (i+1, count, meanr * 100))

if __name__ == '__main__':
  main()

