from dataclasses import dataclass
from typing import List

@dataclass
class Book:
    id: str
    title: str
    author: str = ""
    grade: int = 0
    file_path: str = ""
    topics: List[str] = None
