import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from sync import transform

class SyncTests(unittest.TestCase):
    def test_latest_wins_and_flags_bad_price(self):
        clean, errors = transform([
            {'vendor':'A', 'sku':'a1','price':'10', 'updated_at':'2026-01-01'},
            {'vendor':'A', 'sku':'a1','price':'12', 'updated_at':'2026-01-02'},
            {'vendor':'A', 'sku':'bad','price':'-1', 'updated_at':'2026-01-02'}])
        self.assertEqual(clean[0]['price'], '12.00')
        self.assertEqual(len(errors),1)

if __name__ == '__main__': unittest.main()
