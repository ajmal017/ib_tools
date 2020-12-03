from typing import Tuple, Optional
from dataclasses import dataclass

from ib_insync import ContFuture
from logbook import Logger

from streamers import VolumeStreamer
from candle import (MultipleBreakoutCandle, BreakoutLockCandle, BreakoutCandle,
                    CarverCandle, RsiCandle)
from portfolio import FixedPortfolio, AdjustedPortfolio, WeightedAdjustedPortfolio
from execution_models import (EventDrivenExecModel, StopMultipleTakeProfit,
                              EventDrivenTakeProfitExecModel)


log = Logger(__name__)


@dataclass
class Params:
    contract: Tuple[str]  # contract given as tuple of params given to Future()
    micro_contract: Tuple[str]  # (1/10) contract corresponding to contract
    periods: int = 40  # periods for breakout calculation
    ema_fast: int = 5  # number of periods for moving average filter
    ema_slow: int = 120  # number of periods for moving average filter
    sl_atr: int = 1  # stop loss in ATRs
    atr_periods: int = 180  # number of periods to calculate ATR on
    trades_per_day: int = 0
    alloc: float = 0  # fraction of capital to be allocated to instrument
    # candle volume to be calculated as average of x periods
    avg_periods: Optional[int] = None
    volume: Optional[int] = None  # candle volume given directly
    min_atr: float = 0
    rsi_threshold: float = 70
    rsi_periods: float = 24
    rsi_smooth: float = 15
    lock_periods_multiple: float = 2
    tp_multiple: float = 2

    def __post_init__(self) -> None:
        self.lock_periods = int(self.periods / self.lock_periods_multiple)


nq = Params(
    contract=ContFuture('NQ', 'GLOBEX'),
    micro_contract=ContFuture('MNQ', 'GLOBEX'),
    trades_per_day=5,
    atr_periods=50,
    # avg_periods=60,
    volume=12000,
    min_atr=14,
    alloc=.3,
    tp_multiple=6,
)

es = Params(
    contract=ContFuture('ES', 'GLOBEX'),
    micro_contract=ContFuture('MES', 'GLOBEX'),
    trades_per_day=.8,
    ema_fast=120,
    ema_slow=320,
    sl_atr=3,
    # avg_periods=60,
    volume=43000,
    min_atr=5,
    alloc=.2,
    lock_periods_multiple=1,
    tp_multiple=3
)

gc = Params(
    contract=ContFuture('GC', 'NYMEX'),
    micro_contract=ContFuture('MGC', 'NYMEX'),
    trades_per_day=1.7,
    ema_fast=60,
    periods=60,
    sl_atr=2,
    # atr_periods=90,
    atr_periods=50,
    # avg_periods=60,
    volume=5500,
    min_atr=1.9,
    alloc=.2,
)

ym = Params(
    contract=ContFuture('YM', 'ECBOT'),
    micro_contract=ContFuture('MYM', 'ECBOT'),
    trades_per_day=.9,
    atr_periods=50,
    ema_fast=60,
    ema_slow=120,
    sl_atr=2,
    # avg_periods=60,
    volume=8000,
    alloc=.3,
    tp_multiple=6
)


# contracts = [es, gc]

exec_model = EventDrivenTakeProfitExecModel()

candles = [BreakoutLockCandle(VolumeStreamer(params.volume,
                                             params.avg_periods),
                              contract_fields=[
    'contract', 'micro_contract'],
    **params.__dict__)
    for params in [es, ym, gc]]

candles.append(BreakoutCandle(VolumeStreamer(nq.volume,
                                             nq.avg_periods),
                              contract_fields=['contract', 'micro_contract'],
                              **nq.__dict__))


portfolio = AdjustedPortfolio(target_vol=.55)

strategy_kwargs = {'candles': candles,
                   'portfolio': portfolio,
                   'exec_model': exec_model}