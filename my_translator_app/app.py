from flask import Flask, render_template, request
from googletrans import Translator
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from flask_mail import Mail, Message
import os


# Create the translator instance
translator = Translator()
# Define supported languages
languages = {
    'en': 'English', 'zh-cn': 'Chinese', 'es': 'Spanish', 'hi': 'Hindi',
    'ar': 'Arabic', 'bn': 'Bengali', 'pt': 'Portuguese', 'ru': 'Russian',
    'ja': 'Japanese', 'pa': 'Punjabi'
}

app = Flask(__name__)


# Email Configuration (using Gmail as an example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('israel41026@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('A4102647')
app.config['MAIL_DEFAULT_SENDER'] = 'israel41026@gmail.com'

# Initialize Flask-Mail
mail = Mail(app)

def detect_language(text):
    return translator.detect(text).lang

def is_nonsense(text):
    return len(text.split()) < 3

def get_simple_synonym(word):
    synonyms = wordnet.synsets(word)
    if not synonyms:
        return word

    for synonym in synonyms:
        # Check if the synonym is an adjective, verb, or noun (to avoid proper names)
        if synonym.pos() in ['n', 'v', 'a', 'r']:
            for lemma in synonym.lemmas():
                simpler_word = lemma.name()
                # Avoid replacing with words that are too specific or proper names
                if simpler_word.lower() != word.lower() and '_' not in simpler_word:
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
    simple_words = []
    for word in words:
        simple_word = get_simple_synonym(word.lower())
        if simple_word != word.lower():
            simple_words.append(f"{word} ({simple_word})")
        else:
            simple_words.append(word)
    return ' '.join(simple_words)

@app.route("/", methods=["GET", "POST"])
def index():
    simplified_text = ""
    detected_language = ""
    user_text = ""  # Variable to store user input

    if request.method == "POST":
        user_text = request.form["text"]  # Get user input

        if is_nonsense(user_text):
            return render_template("index.html", error="Please enter a real sentence.", user_text=user_text)

        detected_language = detect_language(user_text)

        if detected_language not in languages:
            return render_template("index.html", error=f"Language '{detected_language}' is not supported.", user_text=user_text)

        simplified_text = simplify_text(user_text, detected_language)

    return render_template("index.html", languages=languages, simplified_text=simplified_text, detected_language=detected_language, user_text=user_text)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Get data from the form
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Compose the email
        msg = Message(
            subject=f"Contact Form Submission from {name}",
            sender=email,
            recipients=["israel41026@gmail.com"],  # Replace with your email
            body=f"Message from {name} ({email}):\n\n{message}"
        )

        # Send the email
        mail.send(msg)

        return render_template("contact.html", success=True)  # Display success message

    return render_template("contact.html")

@app.route("/contribute")
def contribute():
    return render_template("contribute.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=False)
