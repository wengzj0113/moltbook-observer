import requests
import collector
import importlib
importlib.reload(collector)
from collector import translate_text

def test_translation_engine():
    print("Testing Translation Engine...")
    sample_text = "The quick brown fox jumps over the lazy dog."
    targets = ['zh-CN', 'fr', 'ja', 'it', 'ru', 'ko', 'es']
    
    for lang in targets:
        try:
            print(f"Translating to {lang}...", end=" ")
            res = translate_text(sample_text, target=lang)
            if res and res != sample_text:
                print(f"OK: {res}")
            else:
                print("FAILED (Returned None or same text)")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_translation_engine()
