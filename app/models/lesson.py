from dataclasses import dataclass
from typing import List

@dataclass
class LessonPlan:
    topic: str
    lesson_type: int  # 1,2,3
    summary: str
    presentation_slides: List[dict]  # [{"title": str, "content": str}]
    classwork: List[str]
    homework: List[str]
