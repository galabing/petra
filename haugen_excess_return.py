#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path

PRICE_BONUS = 0.01
MIN_CAP = -1.0
MAX_CAP = 1.0

def read_samples(file_path):
  with open(file_path, 'r') as fp:
    lines = fp.read().splitlines()
  d = dict()
  for line in lines:
    dt, vo, pr = line.split(' ')
    pr = float(pr)
    d[dt[:7]] = pr
  return d

# Computes the yyyy-mm string that is delta months before the current yyyy-mm
# string.
def compute_date(current_date, delta):
  y, m = current_date.split('-')
  y, m = int(y), int(m)
  yd = int(delta / 12)
  md = delta % 12
  y -= yd
  m -= md
  if m < 1:
    y -= 1
    m += 12
  return '%04d-%02d' % (y, m)

def compute_excess(stock_from, stock_to, market_from, market_to,
                   bonus=PRICE_BONUS, min_cap=MIN_CAP, max_cap=MAX_CAP):
  assert stock_from >= 0
  assert stock_to >= 0
  assert market_from >= 0
  assert market_to >= 0
  assert bonus > 0  # bonus must be positive to prevent divide-by-zero errors.
  stock_r = (stock_to - stock_from) / (stock_from + bonus)
  market_r = (market_to - market_from) / (market_from + bonus)
  excess = stock_r - market_r
  if excess > max_cap: return max_cap
  if excess < min_cap: return min_cap
  return excess

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--price_sample_dir', required=True)
  parser.add_argument('--market_sample_path', required=True)
  parser.add_argument('--yyyy_mm', required=True)
  parser.add_argument('--k', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)
  k = int(args.k)
  assert k > 0

  market_samples = read_samples(args.market_sample_path)
  curr_date = args.yyyy_mm
  prev_date = compute_date(curr_date, k)
  logging.info('current date = %s, previous date = %s' % (curr_date, prev_date))
  assert curr_date in market_samples
  assert prev_date in market_samples

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  excess_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    assert ticker.find('^') == -1  # ^GSPC should not be in tickers.
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    stock_sample_path = '%s/%s.csv' % (args.price_sample_dir, ticker)
    if not path.isfile(stock_sample_path):
      logging.warning('Input file does not exist: %s' % stock_sample_path)
      continue
    stock_samples = read_samples(stock_sample_path)
    if (curr_date not in stock_samples
        or prev_date not in stock_samples):
      logging.warning('Insufficient data for %s' % ticker)
      continue
    excess = compute_excess(
        stock_samples[prev_date], stock_samples[curr_date],
        market_samples[prev_date], market_samples[curr_date])
    excess_map[ticker] = excess
  with open(args.output_path, 'w') as fp:
    for ticker in sorted(excess_map.keys()):
      print('%s %f' % (ticker, excess_map[ticker]), file=fp)

if __name__ == '__main__':
  main()



