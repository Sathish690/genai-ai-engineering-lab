import unittest
from hybrid_rag.models import Document, SearchResult
from hybrid_rag.retrievers import BM25Retriever, reciprocal_rank_fusion

class RetrievalTests(unittest.TestCase):
 def setUp(self): self.docs=[Document("a","cancel policy permits refund","a.txt"),Document("b","network security guide","b.txt")]
 def test_bm25_returns_keyword_match(self): self.assertEqual(BM25Retriever(self.docs).search("refund policy",1)[0].document.id,"a")
 def test_rrf_rewards_agreement(self):
  a,b=self.docs; result=reciprocal_rank_fusion([[SearchResult(a,1,"bm25"),SearchResult(b,.8,"bm25")],[SearchResult(a,.7,"vector")]],2)
  self.assertEqual(result[0].document.id,"a"); self.assertEqual(result[0].retriever,"rrf")
 def test_rrf_rejects_bad_top_k(self):
  with self.assertRaises(ValueError): reciprocal_rank_fusion([],0)
