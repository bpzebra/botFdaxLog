import logging
import csv
import datetime
import os
from ib_insync import IB, Future, util

# Configuration
HOST = '127.0.0.1'
PORT = 4002 # 7497  # Default TWS paper trading port. Use 7496 for live.
CLIENT_ID = 1
LOG_FILE = 'trades_log.csv'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FDAXLogger:
    def __init__(self, host=HOST, port=PORT, client_id=CLIENT_ID, log_file=LOG_FILE):
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
        self.log_file = log_file

        # Ensure CSV header exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'tradeprice', 'tradevolume'])

    def connect(self):
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            logger.info(f"Connected to IB on {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    def get_fdax_contract(self):
        logger.info("Searching for FDAX front-month contract...")
        # Search for FDAX futures on EUREX
        cds = self.ib.reqContractDetails(Future(symbol='FDAX', exchange='EUREX', currency='EUR'))
        if not cds:
            raise ValueError("No FDAX contracts found.")
        
        # Sort by expiration and pick the closest one
        contracts = [cd.contract for cd in cds]
        contracts.sort(key=lambda x: x.lastTradeDateOrContractMonth)
        
        target = contracts[0]
        logger.info(f"Selected contract: {target.localSymbol} (Expiry: {target.lastTradeDateOrContractMonth})")
        return target

    def start_logging(self):
        contract = self.get_fdax_contract()
        self.ib.qualifyContracts(contract)
        
        # Use reqTickByTickData for more accurate trade logging
        # Tick type 'Last' or 'AllLast'
        ticks = self.ib.reqTickByTickData(contract, 'Last')
        
        def on_pending_tick(ticks):
            for tick in ticks:
                # TickByTickAllLast has price, size, time
                self.log_trade(tick.time, tick.price, tick.size)

        self.ib.pendingTickersEvent += on_pending_tick # This is wrong for tick-by-tick
        # Actually reqTickByTickData returns a ticker object which gets updated
        # or we use an event.
        
        # Correct way in ib_insync to handle tick-by-tick:
        def on_tick_event(ticker, ticks):
            for tick in ticks:
                self.log_trade(tick.time, tick.price, tick.size)
        
        # ib.reqTickByTickData(contract, 'Last') will trigger ib.tickByTickEvent
        self.ib.tickByTickEvent += on_tick_event
        
        logger.info("Started logging trades. Press Ctrl+C to stop.")
        try:
            self.ib.run()
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            self.ib.disconnect()

    def log_trade(self, timestamp, price, volume):
        # Format timestamp to ISO
        ts_str = timestamp.isoformat() if isinstance(timestamp, datetime.datetime) else str(timestamp)
        logger.info(f"Trade: {ts_str}, {price}, {volume}")
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ts_str, price, volume])

if __name__ == "__main__":
    bot = FDAXLogger()
    try:
        bot.connect()
        bot.start_logging()
    except Exception as e:
        logger.error(f"Error: {e}")
