import nltk
from textblob import TextBlob
import json
import random
import pickle
import numpy as np
import requests
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
from flask import Flask, render_template, request
import re
from datetime import datetime
import csv

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize
lemmatizer = WordNetLemmatizer()
app = Flask(__name__)
app.static_folder = 'static'

# OpenAI API configuration
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")  # Replace with your OpenAI API key

class MentalHealthBoundaryChecker:
    """Check if user input is within mental health domain"""
    
    def __init__(self):
        # Mental health related keywords
        self.mental_health_keywords = {
            'emotions': ['sad', 'happy', 'angry', 'frustrated', 'excited', 'worried', 'anxious', 
                        'depressed', 'lonely', 'scared', 'stressed', 'overwhelmed', 'hopeless',
                        'worthless', 'empty', 'numb', 'irritated', 'mood', 'feeling', 'feel'],
            
            'mental_health': ['depression', 'anxiety', 'panic', 'therapy', 'counseling', 'mental health',
                             'suicide', 'self harm', 'bipolar', 'ptsd', 'trauma', 'grief', 'loss',
                             'eating disorder', 'addiction', 'substance abuse', 'insomnia', 'sleep'],
            
            'student_life': ['exam', 'test', 'study', 'school', 'college', 'university', 'grade',
                           'assignment', 'homework', 'pressure', 'academic', 'student', 'campus',
                           'dormitory', 'peer pressure', 'bullying', 'friendship', 'relationship'],
            
            'support_seeking': ['help', 'support', 'talk', 'listen', 'advice', 'guidance', 'confused',
                              'lost', 'dont know', "don't know", 'struggling', 'difficult', 'hard time',
                              'need someone', 'alone', 'isolated'],
            
            'coping': ['cope', 'manage', 'deal with', 'handle', 'overcome', 'get through', 'survive',
                      'breathe', 'calm down', 'relax', 'meditation', 'mindfulness', 'exercise'],
            
            'greetings': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                         'how are you', 'whats up', "what's up", 'greetings', 'sup']
        }
        
        # Topics clearly outside mental health domain
        self.non_mental_health_topics = [
            'programming', 'code', 'python', 'java', 'javascript', 'html', 'css', 'sql',
            'fibonacci', 'algorithm', 'data structure', 'machine learning', 'ai',
            'cricket', 'football', 'sports', 'game', 'movie', 'film', 'music', 'song',
            'recipe', 'cooking', 'food', 'weather', 'news', 'politics', 'economics',
            'science', 'physics', 'chemistry', 'biology', 'mathematics', 'history',
            'geography', 'travel', 'vacation', 'shopping', 'fashion', 'technology',
            'car', 'bike', 'transport', 'joke', 'funny', 'meme'
        ]
    
    def is_mental_health_related(self, text):
        """Check if the input is related to mental health or student wellbeing"""
        text_lower = text.lower()
        
        # Check for mental health keywords
        for category, keywords in self.mental_health_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return True, category
        
        # Check for clear non-mental health topics
        for topic in self.non_mental_health_topics:
            if topic in text_lower:
                return False, 'non_mental_health'
        
        # If unclear, assume it might be mental health related (better safe than sorry)
        return True, 'unclear'

def get_openai_response(user_message, matched_intent=None, intent_response=None, context_info=None):
    """Get response from OpenAI API with enhanced mental health context"""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enhanced system prompt with personality
    system_prompt = """You are Mitra, a warm and empathetic mental health support chatbot specifically designed for students. You have the personality of a caring friend who:

- Always prioritizes mental health and student wellbeing
- Speaks naturally like a supportive friend, not a clinical therapist
- Uses simple, conversational language
- Shows genuine empathy and understanding
- Offers practical, student-friendly advice
- Encourages healthy coping mechanisms
- Knows when to suggest professional help
- Maintains appropriate boundaries

IMPORTANT GUIDELINES:
- Keep responses to 2-3 sentences maximum
- Never use markdown, bullet points, or citations
- Stay focused on mental health and student wellbeing topics
- If asked about non-mental health topics (like programming, sports, etc.), gently redirect to mental health
- Use encouraging, supportive tone
- Ask follow-up questions to show engagement

Your goal is to make students feel heard, supported, and less alone in their struggles."""

    # Add context if available
    context = ""
    if matched_intent and intent_response:
        context = f"\nContext: The user's message relates to '{matched_intent}'. You can reference this similar response for guidance: '{intent_response}'. But respond more naturally and personally."
    
    if context_info:
        context += f"\nAdditional context: {context_info}"
    
    user_prompt = f"Student: {user_message}\nMitra:"
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt + context},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 120,
        "temperature": 0.8
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            bot_response = result["choices"][0]["message"]["content"].strip()
            return clean_response(bot_response)
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return get_fallback_response(matched_intent, intent_response)
    except Exception as e:
        print(f"OpenAI API exception: {str(e)}")
        return get_fallback_response(matched_intent, intent_response)

def clean_response(response):
    """Clean up response formatting and ensure it's conversational"""
    # Remove markdown formatting
    response = re.sub(r'\*\*.*?\*\*', lambda m: m.group(0).replace('**', ''), response)
    response = response.replace('*', '')
    response = response.replace('#', '')
    response = response.replace('```', '')
    response = response.replace('`', '')
    
    # Remove citations and references
    response = re.sub(r'\[\d+\]', '', response)
    response = re.sub(r'\[.*?\]', '', response)
    
    # Remove "Mitra:" prefix if it exists
    if response.startswith("Mitra:"):
        response = response[6:].strip()
    
    # Limit to reasonable length (2-3 sentences)
    sentences = response.split('. ')
    if len(sentences) > 3:
        response = '. '.join(sentences[:3]) + '.'
    
    # Remove any remaining formatting
    response = re.sub(r'\n+', ' ', response)
    response = re.sub(r'\s+', ' ', response)
    
    return response.strip()

def get_fallback_response(matched_intent=None, intent_response=None):
    """Enhanced fallback responses based on intent"""
    if matched_intent:
        if 'sad' in matched_intent or 'depressed' in matched_intent:
            return "I can hear that you're going through a tough time right now. Would you like to talk about what's been weighing on your mind?"
        elif 'anxious' in matched_intent or 'stressed' in matched_intent:
            return "It sounds like you're feeling pretty overwhelmed. That's completely understandable - want to share what's been stressing you out?"
        elif 'greeting' in matched_intent:
            return "Hey there! I'm really glad you decided to reach out today. How are you feeling right now?"
        elif intent_response:  # Use intent response if available
            return intent_response
    
    supportive_responses = [
        "I'm here to listen and support you. What's been on your mind lately?",
        "It takes courage to reach out, and I'm glad you did. How can I support you today?",
        "I can sense you might be going through something. Want to talk about it?",
        "You're not alone in whatever you're facing. How are you feeling right now?",
        "I'm here for you. What would help you feel a bit better today?"
    ]
    return random.choice(supportive_responses)

# Load the model and data
try:
    model = load_model('model.h5')
    intents = json.loads(open('intents_master.json').read())  # FIXED: Use correct filename
    words = pickle.load(open('texts.pkl','rb'))
    classes = pickle.load(open('labels.pkl','rb'))
    
    # Load FAQ answers
    faq_answers = {}
    with open('data/Mental_Health_FAQ_cleaned.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row.get('Questions', '').strip().lower()
            a = row.get('Answers', '').strip()
            if q and a:
                faq_answers[q] = a
                
    print("Model and data loaded successfully!")
    print(f"Model recognizes {len(classes)} intent classes")
    print(f"Vocabulary size: {len(words)} words")
    print(f"Loaded {len(faq_answers)} FAQ entries")
except Exception as e:
    print(f"Error loading model/data: {e}")
    model, intents, words, classes, faq_answers = None, None, None, None, {}

# Initialize boundary checker
boundary_checker = MentalHealthBoundaryChecker()

def clean_up_sentence(sentence):
    """Tokenize and lemmatize the sentence"""
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    """Create bag of words array with sentiment features"""
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    
    # Add sentiment features (matching training data)
    blob = TextBlob(sentence)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    bag.append(polarity)
    bag.append(subjectivity)
    
    return np.array(bag)

def predict_class(sentence, model):
    """Predict the class/intent of the sentence"""
    if not model or not words or not classes:
        return []
    
    try:
        p = bow(sentence, words, show_details=False)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        return return_list
    except Exception as e:
        print(f"Error in predict_class: {e}")
        return []

def get_intent_response(ints, intents_json):
    """Get response based on predicted intent with enhanced handling"""
    if not ints or not intents_json:
        return None, None
        
    tag = ints[0]['intent']
    confidence = float(ints[0]['probability'])
    
    print(f"Predicted intent: {tag} (confidence: {confidence:.3f})")
    
    # Handle specific mental health intents with more context
    if tag == 'suicide' or tag == 'crisis_support':
        return tag, ("I'm really concerned about you right now. Please reach out to a crisis helpline immediately - call 988 or text 'HELLO' to 741741. You matter and there are people who want to help.")
    
    elif tag == 'depressed' or tag == 'sad':
        return tag, ("It sounds like you're going through a really difficult time. These feelings can be overwhelming, but you don't have to face them alone. What's been weighing on your mind?")
    
    elif tag == 'anxious' or tag == 'stressed':
        return tag, ("I can hear that you're feeling really overwhelmed right now. Anxiety can be exhausting. Would you like to try a quick breathing exercise together, or do you want to talk about what's causing the stress?")
    
    elif tag == 'faq' and faq_answers:
        # Try to match user question to FAQ
        user_text = " ".join([pattern for intent in intents_json.get('intents', []) 
                             if intent.get('tag') == tag 
                             for pattern in intent.get('patterns', [])])
        for faq_q, faq_a in faq_answers.items():
            if any(word in user_text.lower() for word in faq_q.split()[:3]):
                return tag, faq_a[:200] + "..." if len(faq_a) > 200 else faq_a
    
    # Default intent handling
    list_of_intents = intents_json.get('intents', [])
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            return tag, result
            
    return None, None

def analyze_sentiment(text):
    """Enhanced sentiment analysis with more categories"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Categorize sentiment more specifically
    if polarity < -0.6:
        return 'very_negative', polarity, subjectivity
    elif polarity < -0.2:
        return 'negative', polarity, subjectivity
    elif polarity < 0.2:
        return 'neutral', polarity, subjectivity
    elif polarity < 0.6:
        return 'positive', polarity, subjectivity
    else:
        return 'very_positive', polarity, subjectivity

def detect_crisis_keywords(text):
    """Detect crisis situations that need immediate attention"""
    crisis_keywords = [
        'kill myself', 'end my life', 'suicide', 'want to die', 'kill me',
        'hurt myself', 'self harm', 'cut myself', 'overdose', 'jump off'
    ]
    
    text_lower = text.lower()
    for keyword in crisis_keywords:
        if keyword in text_lower:
            return True
    return False

def chatbot_response(msg):
    """Enhanced chatbot response with better balance between model and API"""
    try:
        print(f"\n--- Processing message: '{msg}' ---")
        
        # Crisis detection first
        if detect_crisis_keywords(msg):
            return ("I'm very worried about you right now. Please reach out for immediate help - call 988 (Suicide & Crisis Lifeline) or text 'HELLO' to 741741. You're not alone, and there are people who care about you and want to help.")
        
        # Check if message is mental health related
        is_mh_related, category = boundary_checker.is_mental_health_related(msg)
        
        if not is_mh_related and category == 'non_mental_health':
            return ("I'm here specifically to support your mental health and wellbeing as a student. While I'd love to chat about everything, I'm most helpful when we focus on how you're feeling and what's going on in your life. Is there anything about your wellbeing you'd like to talk about?")
        
        # Sentiment analysis
        sentiment_category, polarity, subjectivity = analyze_sentiment(msg)
        print(f"Sentiment: {sentiment_category} (polarity: {polarity:.2f}, subjectivity: {subjectivity:.2f})")
        
        # Intent classification
        matched_intent = None
        intent_response = None
        confidence = 0.0
        
        if model and intents:
            ints = predict_class(msg, model)
            if ints:
                matched_intent, intent_response = get_intent_response(ints, intents)
                confidence = float(ints[0]['probability'])
                print(f"Intent match: {matched_intent} (confidence: {confidence:.3f})")
        
        # ENHANCED DECISION LOGIC: When to use model vs API
        use_model_response = False
        
        # Use model response if:
        # 1. High confidence intent match (>0.7)
        # 2. Specific mental health intents that have good responses
        # 3. Crisis situations (already handled above)
        if confidence > 0.7 and matched_intent:
            specific_intents = ['greeting', 'thanks', 'goodbye', 'depressed', 'anxious', 
                              'suicide', 'crisis_support', 'breathing_exercise']
            if matched_intent in specific_intents:
                use_model_response = True
                print("Using model response (high confidence + specific intent)")
        
        # For medium confidence (0.4-0.7), blend model and API
        elif 0.4 <= confidence <= 0.7 and matched_intent and intent_response:
            print("Using API with model context (medium confidence)")
            context_info = f"Sentiment: {sentiment_category}, Intent: {matched_intent}, Confidence: {confidence:.3f}"
            response = get_openai_response(msg, matched_intent, intent_response, context_info)
        
        # For low confidence (<0.4), use pure API but with mental health context
        else:
            print("Using pure API response (low/no intent confidence)")
            context_info = f"Sentiment: {sentiment_category}, Category: {category}"
            response = get_openai_response(msg, context_info=context_info)
        
        # Execute model response if decided
        if use_model_response and intent_response:
            response = intent_response
            print("Using direct model response")
        
        # Add sentiment-appropriate modifications
        if sentiment_category in ['very_negative', 'negative']:
            if not any(word in response.lower() for word in ['sorry', 'understand', 'hear', 'difficult']):
                if 'crisis' not in response.lower() and 'helpline' not in response.lower():
                    response = "I can hear that you're really struggling right now. " + response
        
        # Ensure response quality
        if not response or len(response.strip()) < 10:
            response = get_fallback_response(matched_intent, intent_response)
        
        # Final response cleanup
        if len(response.split()) > 50:  # If response is too long
            sentences = response.split('. ')
            response = '. '.join(sentences[:2]) + '.'
        
        print(f"Final response: {response}")
        return response.strip()
        
    except Exception as e:
        print(f"Error in chatbot_response: {str(e)}")
        return "I'm here for you, even if I'm having a technical moment. How are you feeling right now?"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    print(f"\n=== NEW REQUEST ===")
    print(f"User message: {userText}")
    
    if not userText or userText.strip() == "":
        return "I'm here and ready to listen. What's on your mind today?"
    
    try:
        bot_response = chatbot_response(userText.strip())
        print(f"Bot response: {bot_response}")
        print("=== END REQUEST ===\n")
        return bot_response
    except Exception as e:
        print(f"Error getting bot response: {str(e)}")
        return "I'm having a technical moment, but I'm still here for you. How are you feeling today?"

if __name__ == "__main__":
    print("🤖 Starting Enhanced Mental Health Chatbot for Students...")
    print("✅ OpenAI API integration: Active")
    print("✅ Mental health boundary checking: Active")
    print("✅ Crisis detection: Active")
    print("✅ Student-focused responses: Active")
    print("✅ Hybrid Model + API approach: Active")
    
    if model:
        print("✅ Intent classification: Active")
        print(f"   - Model classes: {len(classes)}")
        print(f"   - Vocabulary: {len(words)} words")
    else:
        print("⚠️  Intent classification: Using API only")
        
    if faq_answers:
        print(f"✅ FAQ database: {len(faq_answers)} entries")
    else:
        print("⚠️  FAQ database: Not loaded")
        
    print("🌐 Server starting on http://localhost:5000")
    print("💚 Ready to support student mental health!")
    app.run(debug=True, port=5000)