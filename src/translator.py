import os
import google.generativeai as genai
import time
from typing import List

class Translator:
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("Google API Key is required.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def translate_text(self, text: str) -> str:
        """
        Translates English text to Hinglish using Gemini.
        """
        # 1. Skip strictly numeric or very short text to preserve formatting/numbers
        if not text or not text.strip():
            return text
        if len(text.strip()) < 3 and not text.strip().isalpha():
            return text
        # Skip if it looks like just a number
        try:
            float(text.replace(',', '').strip())
            return text
        except ValueError:
            pass

        prompt = f"""
        You are a professional English-to-Hindi translator. Translate the following text into **Conversational Hinglish** (Hindi written in Roman script).

        **Style Guide**:
        - **Grammar**: Use Hindi grammar (SOV structure usually), but keep the flow natural.
        - **Vocabulary**: Use English for technical nouns (e.g. 'API', 'Database', 'Laser'). Use Hindi for verbs, adjectives, and connecting words where natural (e.g., 'karna', 'hona', 'accha').
        - **Conciseness**: Try to keep the translated length close to the original. Do not add unnecessary filler words.
        - **No Transliteration**: Do not just write English words in Hindi script (e.g., dont write "book" as "buk", writes "kitaab").
        
        **Strict Rules**:
        1. Return ONLY the translated text. DO NOT add "ka matlab hai", "Ye hai", or any conversational filler.
        2. Keep numbers, table of contents, and symbols EXACTLY as is.
        3. Do not translate code or URLs.
        4. If the text is a Table of Contents line (e.g., "1. Introduction ..... 5"), keep the structure and only translate the text part.

        Input Text:
        "{text}"
        """

        try:
            # We add a small delay to avoid hitting rate limits instantly if called in tight loop
            response = self.model.generate_content(prompt)
            translated = response.text.strip()
            
            # 2. Sanity check: If the response is an error message or refusal, return original
            if "I cannot translate" in translated or "loops" in translated or "language model" in translated or "Oops" in translated:
                return text
                
            return translated
        except Exception as e:
            # print(f"Translation error: {e}") # Reduce noise
            return text # Fallback to original text

    def translate_batch(self, texts: List[str]) -> List[str]:
        """
        Translates a batch of texts.
        """
        translated = []
        for t in texts:
            translated.append(self.translate_text(t))
        return translated
