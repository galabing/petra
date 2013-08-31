#!/usr/local/bin/python3

""" Downloads financial data (income statements, balance sheets and cash flow
    statements) from morningstar.com.
"""

import argparse
import logging
import utils
from os import path, remove, stat, system

WGET = '/usr/local/bin/wget'

def download(ticker, report_type, period, output_path):
  url = ('http://financials.morningstar.com/ajax/ReportProcess4CSV.html'
         '?t=%s&region=usa&culture=en-US&cur=USD&reportType=%s&period=%s'
         '&dataType=A&order=asc&columnYear=5&rounding=3&view=raw'
         '&denominatorView=raw&number=3' % (ticker, report_type, period))
  cmd = '%s -q "%s" -O %s' % (WGET, url, output_path)
  if system(cmd) != 0:
    logging.warning('Download failed for %s: %s' % (ticker, url))
    if path.isfile(output_path):
      remove(output_path)
    return False
  if stat(output_path).st_size <= 0:
    logging.warning('Empty downloaded file for %s: %s' % (ticker, url))
    remove(output_path)
    return False
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--report_type', required=True)
  parser.add_argument('--period', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  rt = args.report_type
  assert rt == 'is' or rt == 'bs' or rt == 'cf', (
      'report_type must be one of "is", "bs" and "cf"')
  p = args.period
  assert p == '3' or p == '12', 'period must be "3" or "12"'

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  sl, fl = [], []  # Lists of tickers succeeded/failed to download.
  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    output_path = '%s/%s.csv' % (args.output_dir, ticker)
    dl = False
    if path.isfile(output_path):
      action = 'skipping'
      if args.overwrite:
        remove(output_path)
        action = 'overwriting'
        dl = True
      logging.warning('Output file exists: %s, %s' % (output_path, action))
    else: dl = True

    if dl:
      ok = download(ticker, rt, p, output_path)
      if ok: sl.append(ticker)
      else: fl.append(ticker)
  logging.info('Downloaded %d tickers, failed %d tickers'
               % (len(sl), len(fl)))
  logging.info('Downloaded tickers: %s' % sl)
  logging.info('Failed tickers: %s' % fl)

if __name__ == '__main__':
  main()

