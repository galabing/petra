#!/usr/local/bin/python3

import os
import sys

# Configs.
DATE = '2013-03'  # The date for training data.
MAX_DATE = '2013-07'  # The latest date for groundtruth price data.
TEST_MONTHS = [1, 2, 3, 4, 6, 12]

IDATA_DIR = '../data'
DATA_DIR = '../data/%s' % DATE
CODE_DIR = './'

# Input files.
DI_T = './data/russell3000.txt'
DI_P = '%s/prices' % IDATA_DIR
DI_PS = '%s/prices_ms' % IDATA_DIR
DI_IS = '%s/is_3_p' % IDATA_DIR
DI_BS = '%s/bs_3_p' % IDATA_DIR
DI_CF = '%s/cf_3_p' % IDATA_DIR
DI_MS = '%s/prices_ms/_GSPC.csv' % IDATA_DIR
# Intermediate data files.
D_P = '%s/price.csv' % DATA_DIR
D_TV = '%s/tv.csv' % DATA_DIR  # trading volume
D_MC = '%s/mc.csv' % DATA_DIR  # market cap
D_R = '%s/revenue.csv' % DATA_DIR  # revenue (4 Qs)
D_NI = '%s/ni.csv' % DATA_DIR  # net income (4 Qs)
D_NIC = '%s/nic.csv' % DATA_DIR  # net income for common shareholders (4 Qs)
D_OS = '%s/os.csv' % DATA_DIR  # outstanding shares
D_TA = '%s/ta.csv' % DATA_DIR  # total assets
D_TL = '%s/tl.csv' % DATA_DIR  # total liabilities
D_IA = '%s/ia.csv' % DATA_DIR  # intangible assets
D_PD = '%s/pd.csv' % DATA_DIR  # preferred dividend (4 Qs)
D_TE = '%s/te.csv' % DATA_DIR  # total equity
D_OCF = '%s/ocf.csv' % DATA_DIR  # operating cashflow (4 Qs)
# Factors.
D_ER1 = '%s/er1.csv' % DATA_DIR  # excess return
D_ER2 = '%s/er2.csv' % DATA_DIR
D_ER6 = '%s/er6.csv' % DATA_DIR
D_ER12 = '%s/er12.csv' % DATA_DIR
D_TV2MC = '%s/tv2mc.csv' % DATA_DIR  # trading volume to market cap
D_E2P = '%s/e2p.csv' % DATA_DIR  # earnings to price
D_ROE = '%s/roe.csv' % DATA_DIR  # return on equity
D_B2P = '%s/b2p.csv' % DATA_DIR  # book to price
D_CF2P = '%s/cf2p.csv' % DATA_DIR  # cash flow to price

# For factor computation.
H_P = '%s/haugen_current_price.py' % CODE_DIR
H_METRIC = '%s/haugen_metric.py' % CODE_DIR
H_ER = '%s/haugen_excess_return.py' % CODE_DIR
H_MC = '%s/haugen_mc.py' % CODE_DIR
H_TV = '%s/haugen_trading_volume.py' % CODE_DIR
H_TV2MC = '%s/haugen_tv2mc.py' % CODE_DIR
H_E2P = '%s/haugen_e2p.py' % CODE_DIR
H_ROE = '%s/haugen_roe.py' % CODE_DIR
H_B2P = '%s/haugen_b2p.py' % CODE_DIR
H_CF2P = '%s/haugen_cf2p.py' % CODE_DIR

# Output scores.
D_S = '%s/scores.csv' % DATA_DIR
D_FS = '%s/filtered_scores.csv' % DATA_DIR

# For scoring and measurement.
H_SCORE = '%s/haugen_score.py' % CODE_DIR
H_FILTER = '%s/haugen_filter.py' % CODE_DIR
H_MEASURE = '%s/haugen_measure_error.py' % CODE_DIR

def run(cmd):
  print('running command: %s' % cmd)
  sys.stdout.flush()
  assert os.system(cmd) == 0

def run_metric(input_dir, metric, k, skip_empty, output_path):
  cmd = ('%s --ticker_file=%s --input_dir=%s --metric=%s --yyyy_mm=%s --k=%s'
         ' --output_path=%s' % (H_METRIC, DI_T, input_dir, metric, DATE,
                                k, output_path))
  if skip_empty:
    cmd = '%s --skip_empty' % cmd
  run(cmd)

def run_er(k, output_path):
  run('%s --ticker_file=%s --price_sample_dir=%s --market_sample_path=%s'
      ' --yyyy_mm=%s --k=%s --output_path=%s' % (H_ER, DI_T, DI_PS, DI_MS,
      DATE, k, output_path))

print('started')
print('training data ends at %s' % DATE)

# Current price.
run('%s --ticker_file=%s --price_sample_dir=%s --yyyy_mm=%s --output_path=%s'
    % (H_P, DI_T, DI_PS, DATE, D_P))
# Trading volume.
run('%s --ticker_file=%s --price_dir=%s --yyyy_mm=%s --k=1 --output_path=%s'
    % (H_TV, DI_T, DI_P, DATE, D_TV))
# Outstanding shares.
run_metric(DI_IS, 'outstanding_shares', '1', True, D_OS)
# Revenue.
run_metric(DI_IS, 'revenue', '4', True, D_R)
# Net income.
run_metric(DI_IS, 'net_income', '4', True, D_NI)
# Net income for common shareholders.
run_metric(DI_IS, 'net_income_common', '4', True, D_NIC)
# Preferred dividend.
run_metric(DI_IS, 'preferred_dividend', '4', False, D_PD)
# Total assets.
run_metric(DI_BS, 'total_assets', '1', True, D_TA)
# Total liabilities.
run_metric(DI_BS, 'total_liabilities', '1', True, D_TL)
# Total equity.
run_metric(DI_BS, 'total_equity', '1', True, D_TE)
# Intangible assets.
run_metric(DI_BS, 'intangible_assets', '1', False, D_IA)
# Operating cashflow.
run_metric(DI_CF, 'operating_cashflow', '4', True, D_OCF)

# Excess returns.
run_er('1', D_ER1)
run_er('2', D_ER2)
run_er('6', D_ER6)
run_er('12', D_ER12)
# Trading volume to market cap.
run('%s --trading_volumes_path=%s --prices_path=%s'
    ' --outstanding_shares_path=%s --output_path=%s'
    % (H_TV2MC, D_TV, D_P, D_OS, D_TV2MC))
# Earnings to price.
run('%s --net_income_common_path=%s --prices_path=%s'
    ' --outstanding_shares_path=%s --output_path=%s'
    % (H_E2P, D_NIC, D_P, D_OS, D_E2P))
# Return on equity.
run('%s --net_income_path=%s --total_equity_path=%s --output_path=%s'
    % (H_ROE, D_NI, D_TE, D_ROE))
# Book to price.
run('%s --total_assets_path=%s --intangible_assets_path=%s'
    ' --total_liabilities_path=%s --prices_path=%s'
    ' --outstanding_shares_path=%s --output_path=%s'
    % (H_B2P, D_TA, D_IA, D_TL, D_P, D_OS, D_B2P ))
# Cashflow to price.
run('%s --operating_cashflow_path=%s --preferred_dividend_path=%s'
    ' --prices_path=%s --outstanding_shares_path=%s --output_path=%s'
    % (H_CF2P, D_OCF, D_PD, D_P, D_OS, D_CF2P))

# Score stocks.
run('%s --er1_path=%s --er12_path=%s --tv2mc_path=%s --er2_path=%s'
    ' --e2p_path=%s --roe_path=%s --b2p_path=%s --er6_path=%s'
    ' --cf2p_path=%s --output_path=%s'
    % (H_SCORE, D_ER1, D_ER12, D_TV2MC, D_ER2, D_E2P, D_ROE, D_B2P, D_ER6,
       D_CF2P, D_S))
# Filter scores.
run('%s --prices_path=%s --outstanding_shares_path=%s'
    ' --output_path=%s' % (H_MC, D_P, D_OS, D_MC))
run('%s --scores_path=%s --prices_path=%s --mc_path=%s --output_path=%s'
    % (H_FILTER, D_S, D_P, D_MC, D_FS))

def get_date(date, d):
  y, m = date.split('-')
  y, m = int(y), int(m)
  m += d
  if m > 12:
    m -= 12
    y += 1
  return '%04d-%02d' % (y, m)

# Compare to groundtruth.
dd = []
for m in TEST_MONTHS:
  d = get_date(DATE, m)
  if d <= MAX_DATE:
    dd.append((d, '%s/price_%d.csv' % (DATA_DIR, m)))

for dp in dd:
  d, p = dp
  run('%s --ticker_file=%s --price_sample_dir=%s --yyyy_mm=%s --output_path=%s'
    % (H_P, DI_T, DI_PS, d, p))
for dp in dd:
  d, p = dp
  run('%s --current_prices_path=%s --future_prices_path=%s --scores_path=%s'
      % (H_MEASURE, D_P, p, D_FS))

