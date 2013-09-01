#!/usr/local/bin/python3

""" Metric: trailing 12-month average monthly trading volume
    Method:
    - from target date, count back 12 months
    - for each month, aggregate daily volume * adjclose => monthly volume
    - take average for 12 months' monthly volume

    NOTE: volume is usually defined by number of shares, not number of shares
    times price, but Haugen divides it by market cap, so it doesn't make sense
    if price is not accounted for.  Also, the use of adjclose protects possible
    distortion from stock split, in which case the raw volume will be doubled,
    but the adjclose will be halved, keeping the final output somewhat static.
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
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--yyyy_mm', required=True)
  parser.add_argument('--k', default='12')
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  k = int(args.k)
  assert k > 0

  volume_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    input_path = '%s/%s.csv' % (args.price_dir, ticker.replace('^', '_'))
    if not path.isfile(input_path):
      logging.warning('Input file is missing: %s' % input_path)
      continue

    with open(input_path, 'r') as fp:
      lines = fp.read().splitlines()
    vmap = dict()
    assert len(lines) > 0
    for j in range(1, len(lines)):
      d, o, h, l, c, v, a = lines[j].split(',')
      d = d[:7]
      if args.yyyy_mm < d: continue
      if distance(args.yyyy_mm, d) >= k: break
      v = float(v) * float(a)
      if d in vmap: vmap[d] += v
      else: vmap[d] = v
    assert len(vmap) <= k
    if len(vmap) < k:  #max(1, k/2):
      logging.warning('Could not find enough data for %s' % ticker)
      continue
    volume_map[ticker] = sum(vmap.values()) / len(vmap)

  with open(args.output_path, 'w') as fp:
    for ticker in sorted(volume_map.keys()):
      print('%s %f' % (ticker, volume_map[ticker]), file=fp)

if __name__ == '__main__':
  main()

