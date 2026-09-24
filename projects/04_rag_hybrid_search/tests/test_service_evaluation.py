import unittest
from hybrid_rag.evaluation import EvaluationQuestion, evaluate
from hybrid_rag.models import Document, SearchResult
from hybrid_rag.service import HybridRagService, build_prompt

class FixedRetriever:
 def __init__(self, results): self.results=results
 def search(self, question, top_k): return self.results[:top_k]
class FakeLLM:
 def __init__(self): self.prompt=""
 def answer(self,prompt): self.prompt=prompt; return "supported"
class ServiceTests(unittest.TestCase):
 def setUp(self): self.result=SearchResult(Document("d1","Policy text","guide.md"),.9,"fake")
 def test_prompt_contains_grounding_and_debug_metadata(self):
  prompt=build_prompt("What policy?",[self.result]); self.assertIn("guide.md",prompt); self.assertIn("information was not found",prompt)
 def test_service_fuses_and_calls_mock_llm(self):
  llm=FakeLLM(); answer=HybridRagService(FixedRetriever([self.result]),FixedRetriever([self.result]),llm).ask("policy",1)
  self.assertEqual(answer.text,"supported"); self.assertEqual(answer.results[0].document.id,"d1")
 def test_hit_rate_reports_hits(self):
  service=HybridRagService(FixedRetriever([self.result]),FixedRetriever([]),FakeLLM())
  report=evaluate(service,[EvaluationQuestion("one",["d1"]),EvaluationQuestion("two",["missing"])],1)
  self.assertEqual((report.total,report.hits,report.hit_rate),(2,1,.5))
