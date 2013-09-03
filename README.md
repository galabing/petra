Haugen factors:

1. one month excess return		-0.97		-0.72
2. twelve months excess return		0.52		0.52
3. trading volume / market cap		-0.35		-0.2
4. two months excess return		-0.2		-0.11
5. earnings to price			0.27		0.26
6. return on equity			0.24		0.13
7. book to price			0.35		0.39
8. trading volume trend			-0.1		-0.09
9. six months excess return		0.24		0.19
10. cash flow to price			0.13		0.26
11. var in cash flow to price		-0.11		-0.15

8 is skipped due to unknown formula.
11 is skipped due to too much requirement on historical data (5 years).

1, 2, 4, 9 are computed by the same excess return formula.

3:
	trading volume = monthly dollar amount of trading
	market cap = current price * outstanding shares
Trading volume is calculated by aggregating daily volume * adjclose for the
trailing month.

5:
	earnings = net income available to common shareholders
This should be equivalent to (net income - preferred dividends).
Notice that earnings should be aggregated over the previous four quarters.

6:
	return on equity = net income / total equity
Notice that net income should be aggregated over the previous four quarters.

7:
	book = total assets - intangible assets - total liabilities

10:
	cash flow = operating cash flow - preferred dividends
Notice that cash flow should be aggregated over the previous four quarters.

