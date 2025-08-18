import nltk
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import json
import pickle
import numpy as np
import random
import warnings
import csv
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading NLTK wordnet...")
    nltk.download('wordnet')

# Import TensorFlow/Keras with compatibility handling
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Activation, Dropout
    from tensorflow.keras.optimizers.legacy import SGD
    print(f"Using TensorFlow version: {tf.__version__}")
except ImportError:
    try:
        from keras.models import Sequential
        from keras.layers import Dense, Activation, Dropout
        from keras.optimizers import SGD
        print("Using standalone Keras")
    except ImportError:
        print("Error: Neither TensorFlow nor Keras found!")
        exit(1)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Initialize lists
words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ',']

print("Loading intents_master.json...")  # FIXED: Use correct filename
try:
    with open('intents_master.json', 'r') as file:  # FIXED: Use intents_master.json
        intents = json.load(file)
except FileNotFoundError:
    print("Error: intents_master.json not found!")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON in intents_master.json!")
    exit(1)

print(f"Found {len(intents['intents'])} intents")

# Process intents from intents_master.json
for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern.lower())  # FIXED: Convert to lowercase first
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Add Q&A from Mental_Health_FAQ_cleaned.csv as FAQ intents
faq_tag = 'faq'
faq_count = 0
try:
    with open('data/Mental_Health_FAQ_cleaned.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get('Questions', '').strip()
            # FIXED: Add more meaningful patterns from questions
            if question and len(question) > 10:  # Only meaningful questions
                w = nltk.word_tokenize(question.lower())
                words.extend(w)
                documents.append((w, faq_tag))
                faq_count += 1
                if faq_tag not in classes:
                    classes.append(faq_tag)
    print(f"Added {faq_count} FAQ patterns")
except Exception as e:
    print(f"Error loading Mental_Health_FAQ_cleaned.csv: {e}")

# ENHANCED: Add more comprehensive patterns from Student survey
survey_patterns_added = 0
try:
    with open('data/Student_Mental_health_cleaned.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Enhanced depression patterns
            if row.get('Do you have Depression?', '').strip().lower() == 'yes':
                depression_patterns = [
                    "I have depression", "I am depressed", "I feel depressed",
                    "struggling with depression", "depression is affecting me"
                ]
                for pattern in depression_patterns:
                    w = nltk.word_tokenize(pattern.lower())
                    words.extend(w)
                    documents.append((w, 'depressed'))
                    survey_patterns_added += 1
                if 'depressed' not in classes:
                    classes.append('depressed')
            
            # Enhanced anxiety patterns
            if row.get('Do you have Anxiety?', '').strip().lower() == 'yes':
                anxiety_patterns = [
                    "I have anxiety", "I am anxious", "I feel anxious",
                    "struggling with anxiety", "anxiety is overwhelming me"
                ]
                for pattern in anxiety_patterns:
                    w = nltk.word_tokenize(pattern.lower())
                    words.extend(w)
                    documents.append((w, 'anxious'))
                    survey_patterns_added += 1
                if 'anxious' not in classes:
                    classes.append('anxious')
            
            # Enhanced panic attack patterns
            if row.get('Do you have Panic attack?', '').strip().lower() == 'yes':
                panic_patterns = [
                    "I have panic attacks", "I get panic attacks", "panic attack symptoms",
                    "experiencing panic attacks", "panic disorder"
                ]
                for pattern in panic_patterns:
                    w = nltk.word_tokenize(pattern.lower())
                    words.extend(w)
                    documents.append((w, 'anxious'))  # Map to anxious intent
                    survey_patterns_added += 1
            
            # Enhanced help-seeking patterns
            if row.get('Did you seek any specialist for a treatment?', '').strip().lower() == 'yes':
                help_patterns = [
                    "I need professional help", "should I see a therapist",
                    "need counseling", "seeking specialist help"
                ]
                for pattern in help_patterns:
                    w = nltk.word_tokenize(pattern.lower())
                    words.extend(w)
                    documents.append((w, 'seeking_help'))
                    survey_patterns_added += 1
                if 'seeking_help' not in classes:
                    classes.append('seeking_help')
                    
    print(f"Added {survey_patterns_added} survey-based patterns")
except Exception as e:
    print(f"Error loading Student_Mental_health_cleaned.csv: {e}")

# Lemmatize and lower each word and remove duplicates
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Sort classes
classes = sorted(list(set(classes)))

print(f"Documents: {len(documents)}")
print(f"Classes: {len(classes)}")
print(f"Unique lemmatized words: {len(words)}")
print(f"Intent classes: {classes}")

# Save processed data
pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('labels.pkl', 'wb'))
print("Saved texts.pkl and labels.pkl")

# Create training data
training = []
output_empty = [0] * len(classes)

print("Creating training data...")
for doc in documents:
    # Initialize our bag of words
    bag = []
    # List of tokenized words for the pattern
    pattern_words = doc[0]
    # Lemmatize each word - create base word, in attempt to represent related words
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # Create our bag of words array with 1, if word match found in current pattern
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # FIXED: Add sentiment features but normalize them
    pattern_text = ' '.join(pattern_words)
    if pattern_text.strip():  # Only if we have text
        blob = TextBlob(pattern_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
    else:
        polarity = 0.0
        subjectivity = 0.0
    
    bag.append(polarity)
    bag.append(subjectivity)

    # Output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty)
    if doc[1] in classes:  # FIXED: Safety check
        output_row[classes.index(doc[1])] = 1
    else:
        print(f"Warning: Unknown class {doc[1]}")
        continue

    training.append([bag, output_row])

# Shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training, dtype=object)

# Create train and test lists. X - patterns, Y - intents
train_x = list(training[:, 0])
train_y = list(training[:, 1])

print(f"Training data created: {len(train_x)} samples")

# ENHANCED: Create model with better architecture
print("Building enhanced neural network...")
input_dim = len(train_x[0])
model = Sequential()
model.add(Dense(256, input_shape=(input_dim,), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Use Adam optimizer for better performance
try:
    from tensorflow.keras.optimizers import Adam
    optimizer = Adam(learning_rate=0.001)
except:
    # Fallback to SGD
    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    optimizer = sgd

model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

print("Model compiled successfully")
print(f"Model architecture:")
print(f"- Input layer: {input_dim} features (including sentiment)")
print(f"- Hidden layers: 256 -> 128 -> 64 neurons")
print(f"- Output layer: {len(train_y[0])} classes")
print("Starting training...")

# ENHANCED: Training with validation split and callbacks
try:
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=10,
        min_lr=0.0001
    )
    
    hist = model.fit(
        np.array(train_x), np.array(train_y),
        epochs=300,
        batch_size=8,
        validation_split=0.2,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
except:
    # Fallback without callbacks
    hist = model.fit(
        np.array(train_x), np.array(train_y),
        epochs=200,
        batch_size=5,
        verbose=1
    )

model.save('model.h5')

print("\n" + "="*60)
print("✓ MENTAL HEALTH CHATBOT MODEL TRAINING COMPLETED!")
print("="*60)
print("✓ Files created:")
print("  - model.h5 (trained neural network)")
print("  - texts.pkl (vocabulary)")
print("  - labels.pkl (intent classes)")
print(f"✓ Model trained on {len(documents)} patterns")
print(f"✓ Recognizes {len(classes)} different intent classes")
print(f"✓ Vocabulary size: {len(words)} unique words")
print("="*60)
print("🚀 READY TO LAUNCH!")
print("Run: python app.py")
print("Open: http://localhost:5000")
print("="*60)