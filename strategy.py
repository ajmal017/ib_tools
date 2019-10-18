import sys
import asyncio
from pprint import pprint

from ib_insync import IB, util
from ib_insync.contract import ContFuture, Future
from ib_insync.ibcontroller import IBC, Watchdog
from eventkit import Event


from trader import Candle, Trader, Blotter, get_contracts
from logger import logger


log = logger(__file__[:-3])


class WatchdogHandlers:

    def __init__(self, dog):
        dog.startingEvent += self.onStartingEvent
        dog.startedEvent += self.onStartedEvent
        dog.stoppingEvent += self.onStoppingEvent
        dog.stoppedEvent += self.onStoppedEvent
        dog.softTimeoutEvent += self.onSoftTimeoutEvent
        dog.hardTimeoutEvent += self.onHardTimeoutEvent
        self.dog = dog

    @staticmethod
    def onStartingEvent(*args):
        log.debug(f'StartingEvent {args}')

    @staticmethod
    def onStartedEvent(*args):
        log.debug(f'StartedEvent {args}')

    @staticmethod
    def onStoppingEvent(*args):
        log.debug(f'StoppingEvent {args}')

    @staticmethod
    def onStoppedEvent(*args):
        log.debug(f'StoppedEvent {args}')

    @staticmethod
    def onSoftTimeoutEvent(*args):
        log.debug(f'SoftTimeoutEvent {args}')

    @staticmethod
    def onHardTimeoutEvent(*args):
        log.debug(f'HardTimeoutEvent {args}')


class Strategy(WatchdogHandlers):

    def __init__(self, ib, watchdog, trader, contracts):
        self.contracts = contracts
        ib.connectedEvent += self.onConnected
        ib.errorEvent += self.onError
        ib.updatePortfolioEvent += self.onUpdatePortfolioEvent
        ib.accountSummaryEvent += self.onAccountSummaryEvent
        update = Event().timerange(60, None, 300)
        update += self.onScheduledUpdate
        self.ib = ib
        self.trader = trader
        super().__init__(watchdog)

    def onConnected(self):
        log.debug('connection established')
        self.account = ib.client.getAccounts()[0]
        self.ib.accountSummary()
        self.ib.reqPnL(self.account)

    def onStartedEvent(self, *args):
        log.debug('initializing strategy')
        contracts = get_contracts(self.contracts, self.ib)
        candles = [Candle(contract, self.trader, self.ib)
                   for contract in contracts]

    def onError(self, *args):
        log.error(f'ERROR: {args}')

    def onUpdatePortfolioEvent(self, i):
        report = (i.contract.localSymbol, int(i.realizedPNL), int(i.unrealizedPNL),
                  int(i.realizedPNL + i.unrealizedPNL))
        log.info(f'Portfolio item: {report}')

    def onScheduledUpdate(self, time):
        log.info(f'pnl: {self.ib.pnl()}')

    def onAccountSummaryEvent(self, value):
        tags = ['UnrealizedPnL', 'RealizedPnL', 'FuturesPNL',
                'NetLiquidationByCurrency']
        if value.tag in tags:
            log.info(f'{value.tag}: {value.value}')

    def onCommissionReportEvent(self, trade, fill, report):
        pprint(report)


if __name__ == '__main__':
    contracts = [
        ('NQ', 'GLOBEX'),
        ('ES', 'GLOBEX'),
        ('NKD', 'GLOBEX'),
        ('CL', 'NYMEX'),
        ('GC', 'NYMEX'),
    ]
    util.patchAsyncio()
    # util.logToConsole()
    ibc = IBC(twsVersion=978,
              gateway=True,
              tradingMode='paper',
              )
    ib = IB()

    watchdog = Watchdog(ibc, ib,
                        port='4002',
                        clientId=0,
                        )

    blotter = Blotter()
    trader = Trader(ib, blotter)
    # asyncio.get_event_loop().set_debug(True)
    strategy = Strategy(ib, watchdog, trader, contracts)
    watchdog.start()
    ib.run()
