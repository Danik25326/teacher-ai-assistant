import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'groq/compound-mini')
    BOOKS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'books')
    EXAMPLES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'examples')
    MAX_TEXT_LENGTH = 15000  # макс. символів тексту підручника для відправки в модель
