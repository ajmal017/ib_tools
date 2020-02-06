from trader import Params

nq = Params(
    contract=('NQ', 'GLOBEX'),
    periods=[5, 10, 20, 40, 80, 160],
    ema_fast=5,
    ema_slow=120,
    sl_atr=1,
    atr_periods=180,
    avg_periods=60,
    alloc=0.4)

es = Params(
    contract=('ES', 'GLOBEX'),
    periods=[5, 10, 20, 40, 80, 160],
    ema_fast=120,
    ema_slow=320,
    sl_atr=3,
    atr_periods=180,
    avg_periods=60,
    alloc=0.2)

gc = Params(
    contract=('GC', 'NYMEX'),
    periods=[5, 10, 20, 40, 80, 160],
    ema_fast=5,
    ema_slow=120,
    sl_atr=1,
    atr_periods=180,
    avg_periods=45,
    alloc=0.3)

cl = Params(
    contract=('CL', 'NYMEX'),
    periods=[5, 10, 20, 40, 80, 160],
    ema_fast=30,
    ema_slow=120,
    sl_atr=3,
    atr_periods=180,
    avg_periods=90,
    alloc=0.1)

contracts = [nq, es, gc, cl]