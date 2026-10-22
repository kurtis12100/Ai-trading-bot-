# Bitcoin Paper Trading Bot

An educational, **paper-only** BTC/USD trading prototype. It never places live orders, does not require API keys, and does not guarantee profits.

## Run

Requires Python 3.10+ and internet access.

```bash
python paper_bot.py
```

The script retrieves hourly Kraken candles, excludes the unfinished candle, and uses a 10/30-candle moving-average crossover. It starts with $10,000 simulated cash, spends at most 10% of remaining cash on a buy signal, sells the simulated BTC position on a sell signal, and models 0.1% trading fees. State persists locally in `paper_state.json`.

**Important:** The bot is not deployed or scheduled. It has not been backtested or validated. Results exclude slippage, spread, tax, outages, and other real trading costs. Do not use it to trade real funds without independent testing and review.

## Next steps

Add automated tests, candle timestamps for robust deduplication, historical backtesting, logging, and optional scheduled paper execution. Do not commit credentials or private keys.
