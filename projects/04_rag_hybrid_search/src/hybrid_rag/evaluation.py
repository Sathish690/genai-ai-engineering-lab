from dataclasses import dataclass
from .service import HybridRagService
@dataclass(frozen=True)
class EvaluationQuestion:
    question: str
    expected_ids: list[str]
@dataclass(frozen=True)
class EvaluationReport:
    total: int
    hits: int
    hit_rate: float
def evaluate(service: HybridRagService, questions: list[EvaluationQuestion], top_k: int) -> EvaluationReport:
    hits = sum(any(item.document.id in question.expected_ids for item in service.retrieve(question.question, top_k)) for question in questions)
    return EvaluationReport(len(questions), hits, hits / len(questions) if questions else 0.0)
