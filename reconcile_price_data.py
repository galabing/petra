#!/usr/local/bin/python3

import argparse
import logging
import utils
from os import path, remove

def reconcile(old_input_path, new_input_path, output_path):
  with open(old_input_path, 'r') as fp:
    old_lines = fp.read().splitlines()
  with open(new_input_path, 'r') as fp:
    new_lines = fp.read().splitlines()
  assert len(old_lines) > 1
  assert len(new_lines) > 0
  assert old_lines[0] == new_lines[0]
  od = old_lines[1][:old_lines[1].find(',')]
  with open(output_path, 'w') as fp:
    print(new_lines[0], file=fp)
    for i in range(1, len(new_lines)):
      nd = new_lines[i][:new_lines[i].find(',')]
      if nd <= od:
        break
      print(new_lines[i], file=fp)
    for i in range(1, len(old_lines)):
      print(old_lines[i], file=fp)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--old_download_dir', required=True)
  parser.add_argument('--new_download_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    old_input_path = '%s/%s.csv' % (
        args.old_download_dir, ticker.replace('^', '_'))
    new_input_path = '%s/%s.csv' % (
        args.new_download_dir, ticker.replace('^', '_'))
    if not path.isfile(old_input_path):
      logging.warning('Old file does not exist: %s' % old_input_path)
      continue
    if not path.isfile(new_input_path):
      logging.warning('New file does not exist: %s' % new_input_path)
      continue
    output_path = '%s/%s.csv' % (args.output_dir, ticker.replace('^', '_'))
    if path.isfile(output_path) and not args.overwrite:
      logging.warning(
          'Output file exists and not overwritable: %s' % output_path)
      continue
    reconcile(old_input_path, new_input_path, output_path)

if __name__ == '__main__':
  main()

