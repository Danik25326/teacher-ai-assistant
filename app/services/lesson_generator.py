import os
from typing import List
from app.services.groq_client import GroqClient
from app.services.book_reader import extract_text_from_docx
from app.models.lesson import LessonPlan
from app.config import Config

class LessonGenerator:
    def __init__(self):
        self.groq = GroqClient()
        self.examples = self._load_examples()

    def _load_examples(self) -> List[dict]:
        """Завантажує до 3 прикладів уроків із папки examples."""
        examples = []
        examples_path = Config.EXAMPLES_PATH
        if os.path.exists(examples_path):
            for filename in os.listdir(examples_path):
                if filename.endswith(('.docx', '.txt')):
                    filepath = os.path.join(examples_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        examples.append({"name": filename, "content": content})
                    except:
                        # якщо docx, можна теж прочитати через docx, але для простоти поки txt
                        pass
        return examples[:3]

    async def generate_lesson(self, book_path: str, topic: str, lesson_type: int) -> LessonPlan:
        full_text = extract_text_from_docx(book_path)
        if not full_text:
            raise ValueError("Не вдалося витягти текст із книги")

        if len(full_text) > Config.MAX_TEXT_LENGTH:
            full_text = full_text[:Config.MAX_TEXT_LENGTH]

        # Формуємо few-shot приклади
        examples_text = ""
        for ex in self.examples:
            examples_text += f"--- ПРИКЛАД: {ex['name']} ---\n{ex['content']}\n\n"

        system_prompt = """Ти — досвідчений учитель та методист. Твоє завдання — створити план уроку, презентацію та завдання суворо за наданим підручником і в стилі наведених прикладів. Не додавай інформації, якої немає в підручнику. Формат відповіді — JSON."""

        lesson_type_desc = {1: "ознайомлення з новим матеріалом",
                            2: "практична робота",
                            3: "закріплення"}.get(lesson_type, "урок")

        prompt = f"""Використовуй наведені нижче приклади моїх уроків як зразок стилю та структури:
{examples_text}

Тепер підготуй урок за підручником:
{full_text}

Параметри уроку:
Тема: {topic}
Тип уроку: {lesson_type_desc} (код {lesson_type})

Згенеруй конспект уроку, презентацію (список слайдів із заголовками та вмістом), завдання на уроці та домашнє завдання. Використовуй ТІЛЬКИ матеріал із підручника.

Відповідь має бути у форматі JSON з наступною структурою:
{{
  "summary": "Текст конспекту уроку (детально, з цілями, етапами тощо)",
  "presentation_slides": [
    {{"title": "Заголовок слайда 1", "content": "Вміст слайда 1 (маркований список, текст)"}},
    ...
  ],
  "classwork": ["Завдання 1", "Завдання 2", ...],
  "homework": ["Завдання 1", "Завдання 2", ...]
}}
"""
        response = await self.groq.generate_content(prompt, system_prompt,
                                                    temperature=0.3, max_tokens=3000)

        lesson = LessonPlan(
            topic=topic,
            lesson_type=lesson_type,
            summary=response.get('summary', ''),
            presentation_slides=response.get('presentation_slides', []),
            classwork=response.get('classwork', []),
            homework=response.get('homework', [])
        )
        return lesson
