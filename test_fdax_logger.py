import unittest
from unittest.mock import MagicMock, patch
from fdax_logger import FDAXLogger
import datetime
import os

class TestFDAXLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = 'test_trades_log.csv'
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        with patch('fdax_logger.IB'):
            self.logger_bot = FDAXLogger(log_file=self.log_file)

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_trade_creates_file_and_logs_data(self):
        timestamp = datetime.datetime(2023, 10, 27, 10, 0, 0)
        price = 15000.5
        volume = 5
        
        self.logger_bot.log_trade(timestamp, price, volume)
        
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("timestamp,tradeprice,tradevolume", lines[0])
            self.assertIn("2023-10-27T10:00:00,15000.5,5", lines[1])

    @patch('fdax_logger.IB')
    def test_get_fdax_contract(self, MockIB):
        mock_ib_instance = MockIB.return_value
        
        mock_cd1 = MagicMock()
        mock_cd1.contract.lastTradeDateOrContractMonth = '202312'
        mock_cd1.contract.localSymbol = 'FDAX DEC 23'
        
        mock_cd2 = MagicMock()
        mock_cd2.contract.lastTradeDateOrContractMonth = '202403'
        mock_cd2.contract.localSymbol = 'FDAX MAR 24'
        
        mock_ib_instance.reqContractDetails.return_value = [mock_cd2, mock_cd1]
        
        self.logger_bot.ib = mock_ib_instance
        contract = self.logger_bot.get_fdax_contract()
        
        self.assertEqual(contract.lastTradeDateOrContractMonth, '202312')
        self.assertEqual(contract.localSymbol, 'FDAX DEC 23')

if __name__ == '__main__':
    unittest.main()
