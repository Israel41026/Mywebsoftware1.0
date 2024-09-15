from flask import Flask, render_template, request
from googletrans import Translator
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')
nltk.download('wordnet')

# Create the translator instance
translator = Translator()

# Define supported languages
languages = {
    'en': 'English', 'zh-cn': 'Chinese', 'es': 'Spanish', 'hi': 'Hindi',
    'ar': 'Arabic', 'bn': 'Bengali', 'pt': 'Portuguese', 'ru': 'Russian',
    'ja': 'Japanese', 'pa': 'Punjabi'
}

app = Flask(__name__)

def detect_language(text):
    return translator.detect(text).lang

def is_nonsense(text):
    return len(text.split()) < 3

def get_simple_synonym(word):
    synonyms = wordnet.synsets(word)
    if not synonyms:
        return word

    for synonym in synonyms:
        for lemma in synonym.lemmas():
            simpler_word = lemma.name()
            if simpler_word.lower() != word.lower():
                return simpler_word
    return word

def simplify_text(text, lang):
    if lang == 'en':
        return simplify_english(text)
    else:
        english_text = translator.translate(text, dest='en').text
        simplified_english = simplify_english(english_text)
        return translator.translate(simplified_english, dest=lang).text

def simplify_english(text):
    words = word_tokenize(text)
    simple_words = [get_simple_synonym(word.lower()) for word in words]
    return ' '.join(simple_words)

@app.route("/", methods=["GET", "POST"])
def index():
    simplified_text = ""
    detected_language = ""
    if request.method == "POST":
        text = request.form["text"]

        if is_nonsense(text):
            return render_template("index.html", error="Please enter a real sentence.")

        detected_language = detect_language(text)

        if detected_language not in languages:
            return render_template("index.html", error=f"Language '{detected_language}' is not supported.")

        simplified_text = simplify_text(text, detected_language)

    return render_template("index.html", languages=languages, simplified_text=simplified_text, detected_language=detected_language)

if __name__ == "__main__":
    app.run(debug=True)
