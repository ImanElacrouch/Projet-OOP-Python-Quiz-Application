import json
import random
from typing import List, Dict, Any, Optional, Set

class Question:
    def __init__(self, question: str, choices: List[str], correct: List[str],
                 mode: str = "single", tags: Optional[List[str]] = None):
        self.question = question
        self.choices = list(choices)
        self.correct = list(correct)
        self.mode = mode
        self.tags = tags or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "choices": self.choices,
            "correct": self.correct,
            "mode": self.mode,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Question":
        return cls(
            question=d.get("question", ""),
            choices=d.get("choices", []),
            correct=d.get("correct", []),
            mode=d.get("mode", "single"),
            tags=d.get("tags", []),
        )


class QuestionDataset:
    _instance = None

    def __new__(cls, json_path: str = "quiz_dataset.json"):
        if cls._instance is None:
            cls._instance = super(QuestionDataset, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, json_path: str = "quiz_dataset.json"):
        if getattr(self, "_initialized", False):
            return
        self.json_path = json_path
        self.questions: List[Question] = []
        self._load()
        self._initialized = True

    def _load(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.questions = [Question.from_dict(item) for item in data]
        except Exception:
            self.questions = []

    def get_all_tags(self) -> List[str]:
        tags: Set[str] = set()
        for q in self.questions:
            tags.update(q.tags)
        return sorted(tags)

    def filter_by_tags(self, selected_tags: List[str]) -> List[Question]:
        if not selected_tags:
            return list(self.questions)
        sel = set(selected_tags)
        return [q for q in self.questions if sel.intersection(q.tags)]


class QuizGenerator:
    def __init__(self, dataset: QuestionDataset):
        self.dataset = dataset

    def generate(self, selected_tags: List[str], num_questions: int = 5, shuffle_choices: bool = True) -> List[Question]:
        pool = self.dataset.filter_by_tags(selected_tags)
        if not pool:
            return []
        num = min(num_questions, len(pool))
        selected = random.sample(pool, num)
        for q in selected:
            if shuffle_choices:
                random.shuffle(q.choices)
        return selected


class QuizCorrector:
    @staticmethod
    def score_single(correct: List[str], selected: Optional[str]) -> float:
        if selected is None:
            return 0.0
        return 1.0 if selected in correct else 0.0

    @staticmethod
    def score_multiple(correct: List[str], selected: List[str]) -> float:
        correct_set, selected_set = set(correct), set(selected or [])
        if not correct_set:
            return 0.0
        true_pos = len(correct_set & selected_set)
        false_pos = len(selected_set - correct_set)
        score = (true_pos / len(correct_set)) - (false_pos / len(correct_set))
        return max(0.0, score)

    def correct(self, questions: List[Question], answers: Dict[int, Any]) -> Dict[str, Any]:
        per_q_scores, total = [], 0
        details = []
        for i, q in enumerate(questions):
            ans = answers.get(i)
            s = self.score_single(q.correct, ans) if q.mode == "single" else self.score_multiple(q.correct, ans)
            total += s
            per_q_scores.append(s)
            details.append({
                "index": i,
                "question": q.question,
                "correct": q.correct,
                "selected": ans,
                "score": s,
                "mode": q.mode
            })
        return {
            "per_question_scores": per_q_scores,
            "total_raw": total,
            "total_normalized": total / max(1, len(questions)),
            "details": details
        }
