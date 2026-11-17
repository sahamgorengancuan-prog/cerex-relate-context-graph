import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from engine import QUERIES, STORE, snapshot, task_detail, rows

class RelateGraphProofTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=snapshot()

    def test_persistent_store(self):
        self.assertTrue(STORE.exists())
        self.assertGreater(STORE.stat().st_size,1000)
        self.assertEqual(self.s["relate_version"],"1.0.1")
        self.assertEqual(self.s["verified_query_count"],6)

    def test_real_cypher(self):
        self.assertEqual(len(rows("tasks")),8)
        self.assertEqual(len(rows("topology")),6)
        self.assertEqual(len(rows("missing")),1)
        with self.assertRaises(ValueError): rows("DROP DATABASE")

    def test_synthetic_decisions(self):
        results={x["id"]:x for x in self.s["tasks"]}
        self.assertEqual(self.s["counts"]["permitted"],4)
        self.assertEqual(self.s["counts"]["denied"],4)
        self.assertEqual(results["T-01"]["status"],"PERMITTED")
        self.assertEqual(results["T-02"]["status"],"PERMITTED")
        self.assertEqual(results["T-03"]["status"],"PERMITTED")
        self.assertEqual(results["T-04"]["status"],"DENIED")
        self.assertEqual(results["T-05"]["status"],"DENIED")
        self.assertEqual(results["T-06"]["status"],"DENIED")
        self.assertEqual(results["T-07"]["status"],"PERMITTED")
        self.assertEqual(results["T-08"]["status"],"DENIED")

    def test_owner_permission_and_approval(self):
        t=task_detail("T-04")
        self.assertTrue(any("allowlist" in s for s in t["reasons"]))
        self.assertTrue(any("authorization" in s for s in t["reasons"]))
        self.assertTrue(any("network" in s for s in t["reasons"]))

    def test_dependencies(self):
        self.assertTrue(any("T-99" in s for s in task_detail("T-06")["reasons"]))
        self.assertTrue(any("T-04" in s for s in task_detail("T-08")["reasons"]))

    def test_readonly_integrity(self):
        import hashlib
        before=hashlib.sha256(STORE.read_bytes()).hexdigest()
        for _ in range(3): snapshot()
        after=hashlib.sha256(STORE.read_bytes()).hexdigest()
        self.assertEqual(before,after)

    def test_boundary(self):
        self.assertEqual(self.s["status"],"READ_ONLY_PREFLIGHT_NOT_EXECUTION")
        self.assertTrue(all(t["predicted_only"] for t in self.s["tasks"]))
        self.assertIn("synthetic",self.s["data_provenance"].lower())

if __name__=="__main__":unittest.main()
