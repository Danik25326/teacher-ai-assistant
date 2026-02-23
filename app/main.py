import os
import asyncio
from flask import Flask, render_template, request, send_file, jsonify
from app.services.book_reader import extract_topics_from_docx
from app.services.lesson_generator import LessonGenerator
from app.services.ppt_generator import create_presentation
from app.services.doc_generator import create_lesson_doc
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_books_list():
    """Сканує папку books і повертає список книг з темами."""
    books = []
    books_path = Config.BOOKS_PATH
    if os.path.exists(books_path):
        for filename in os.listdir(books_path):
            if filename.endswith('.docx'):
                filepath = os.path.join(books_path, filename)
                topics = extract_topics_from_docx(filepath)
                # Намагаємося витягти клас з імені (можна доробити)
                grade = 0
                if 'клас' in filename.lower():
                    parts = filename.split()
                    for part in parts:
                        if part.isdigit():
                            grade = int(part)
                            break
                books.append({
                    'id': filename,
                    'title': filename.replace('.docx', ''),
                    'grade': grade,
                    'file_path': filepath,
                    'topics': topics
                })
    return books

@app.route('/')
def index():
    books = get_books_list()
    return render_template('index.html', books=books)

@app.route('/api/book/<book_id>/topics')
def book_topics(book_id):
    books = get_books_list()
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify({'topics': book['topics']})
    return jsonify({'topics': []})

@app.route('/generate', methods=['POST'])
def generate():
    book_id = request.form.get('book_id')
    topic = request.form.get('topic')
    lesson_type = int(request.form.get('lesson_type', 1))

    books = get_books_list()
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return "Книгу не знайдено", 404

    generator = LessonGenerator()
    # Запускаємо асинхронну генерацію в синхронному Flask
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        lesson = loop.run_until_complete(generator.generate_lesson(book['file_path'], topic, lesson_type))
    finally:
        loop.close()

    # Зберігаємо у тимчасові файли
    ppt_filename = f"temp/lesson_{book_id}_{topic}.pptx"
    doc_filename = f"temp/lesson_{book_id}_{topic}.docx"
    os.makedirs('temp', exist_ok=True)

    create_presentation(lesson.presentation_slides, ppt_filename)
    create_lesson_doc(lesson, doc_filename)

    return render_template('result.html', lesson=lesson, ppt_file=ppt_filename, doc_file=doc_filename)

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
