import unittest
from src.knowledge_base import EducationalKnowledgeBase, evaluate_retrieval, load_registry

class KnowledgeBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = EducationalKnowledgeBase()
        cls.registry = load_registry()

    def test_only_reviewed_official_sources_are_indexed(self):
        self.assertTrue(self.kb.documents)
        self.assertTrue(all(x["status"] == "verified_snippet" and x["source_url"] and x["verified_notes"] for x in self.kb.documents))

    def test_cambridge_source_ranks_first(self):
        results = self.kb.search("How are Cambridge grade thresholds decided?")
        self.assertTrue(results)
        self.assertEqual(results[0]["source_id"], "cambridge-awarding")

    def test_jurisdiction_filter(self):
        results = self.kb.search("SSCE examination", jurisdiction="Nigeria")
        self.assertTrue(results)
        self.assertTrue(all(x["jurisdiction"] == "Nigeria" for x in results))

    def test_empty_and_unmatched_queries_abstain(self):
        self.assertEqual(self.kb.search(""), [])
        self.assertEqual(self.kb.search("quantum submarine banana"), [])

    def test_retrieval_metrics_are_bounded(self):
        cases = [{"case_id":"a","query":"Cambridge grade thresholds","expected_source_ids":["cambridge-awarding"]}]
        report = evaluate_retrieval(self.kb, cases, top_k=3)
        self.assertEqual(report["total_cases"], 1)
        self.assertGreaterEqual(report["recall_at_k"], 0)
        self.assertLessEqual(report["recall_at_k"], 1)

    def test_pending_system_is_not_mislabelled_verified(self):
        row = next(x for x in self.registry["coverage"] if x["system"] == "Punjab BISE boards")
        self.assertEqual(row["status"], "discovery_pending")

if __name__ == "__main__":
    unittest.main()
