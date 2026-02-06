import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 强制 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

# 将项目目录加入 path
project_root = os.path.abspath(os.path.join(os.getcwd(), "."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 模拟 mcp 依赖，防止导入 server.py 时出错（如果 tx_builder 引用了它）
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

from tron_mcp_server.tx_builder import (
    check_sender_balance, 
    check_recipient_status, 
    build_unsigned_tx, 
    InsufficientBalanceError
)

class TestTxBuilder(unittest.TestCase):

    @patch('tron_mcp_server.tron_client.get_balance_trx')
    @patch('tron_mcp_server.tron_client.get_usdt_balance')
    def test_check_sender_balance_usdt_success(self, mock_usdt, mock_trx):
        # 场景：USDT 充足，TRX 充足
        mock_trx.return_value = 100.0
        mock_usdt.return_value = 50.0
        
        result = check_sender_balance("TAddress", 20.0, "USDT")
        self.assertTrue(result["sufficient"])
        self.assertEqual(result["balances"]["usdt"], 50.0)

    @patch('tron_mcp_server.tron_client.get_balance_trx')
    @patch('tron_mcp_server.tron_client.get_usdt_balance')
    def test_check_sender_balance_usdt_fail_balance(self, mock_usdt, mock_trx):
        # 场景：USDT 余额不足
        mock_trx.return_value = 100.0
        mock_usdt.return_value = 10.0
        
        with self.assertRaises(InsufficientBalanceError) as cm:
            check_sender_balance("TAddress", 20.0, "USDT")
        
        self.assertIn("USDT 余额不足", str(cm.exception))
        self.assertEqual(cm.exception.error_code, "insufficient_usdt")

    @patch('tron_mcp_server.tron_client.get_balance_trx')
    @patch('tron_mcp_server.tron_client.get_usdt_balance')
    def test_check_sender_balance_usdt_fail_gas(self, mock_usdt, mock_trx):
        # 场景：USDT 足，但 TRX 不足以支付 Gas (420 * 65000 = 27.3 TRX)
        mock_trx.return_value = 5.0 
        mock_usdt.return_value = 50.0
        
        with self.assertRaises(InsufficientBalanceError) as cm:
            check_sender_balance("TAddress", 20.0, "USDT")
        
        self.assertIn("TRX 余额不足以支付 Gas", str(cm.exception))

    @patch('tron_mcp_server.tron_client.get_balance_trx')
    def test_check_sender_balance_trx_success(self, mock_trx):
        # 场景：TRX 原生转账充足
        mock_trx.return_value = 50.0
        result = check_sender_balance("TAddress", 10.0, "TRX")
        self.assertTrue(result["sufficient"])

    @patch('tron_mcp_server.tron_client.get_account_status')
    def test_check_recipient_status_warnings(self, mock_status):
        # 场景：接收方未激活且无 TRX
        mock_status.return_value = {
            "is_activated": False,
            "has_trx": False
        }
        
        result = check_recipient_status("TRecipient")
        self.assertTrue(result["checked"])
        self.assertEqual(len(result["warnings"]), 2)
        self.assertIn("⚠️ 预警", result["warning_message"])

    @patch('tron_mcp_server.tron_client.get_latest_block_info')
    @patch('tron_mcp_server.tx_builder.check_sender_balance')
    @patch('tron_mcp_server.tx_builder.check_recipient_status')
    def test_build_unsigned_tx_integration(self, mock_recipient, mock_sender, mock_block):
        # 模拟基础信息
        mock_block.return_value = {"number": 1234567, "hash": "000000000012d687b8f9..."}
        mock_sender.return_value = {"sufficient": True, "balances": {"trx": 100}}
        mock_recipient.return_value = {"warnings": [], "warning_message": None}
        
        # 使用真实的合规 TRON 地址进行测试
        # Binance Hot Wallet 3: TMJJM7C6e92h8Cj4a7E6m2r8k3y5e6h8g
        # USDT Contract: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
        from_addr = "TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9"
        to_addr = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        
        result = build_unsigned_tx(from_addr, to_addr, 10.0, "USDT")
        
        self.assertIn("txID", result)
        self.assertIn("raw_data", result)
        self.assertIn("sender_check", result)
        self.assertIn("recipient_check", result)

if __name__ == '__main__':
    unittest.main()
