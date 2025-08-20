Mental Health Conversational AI Chatbot (Healthcare)

Project Overview:
This project is an advanced AI-powered chatbot designed to provide emotional support, guidance, and information to individuals facing mental health challenges. It uses state-of-the-art Natural Language Processing (NLP) and generative AI to deliver context-aware, multilingual, and empathetic conversations. The chatbot is suitable for healthcare, education, and support sectors, and can be extended for broader conversational AI use cases.

Key Features:
- Conversational AI: Generates smart, context-aware replies using OpenAI API (GPT-3.5-turbo model).
- Multilingual Support: Handles English and Hindi natively, with automatic language detection and translation.
- Sentiment & Topic Analysis: Uses Hugging Face models for sentiment detection and topic classification.
- Intent Recognition: Supports intent-based fallback using a trained Keras/TensorFlow model.
- Healthcare Ready: Can be extended for healthcare-specific queries, symptom triage, and resource guidance.
- Modern UI: Simple web interface for easy interaction.

Architecture & Technologies:
Backend: Python 3.8, Flask
NLP: Hugging Face Transformers, spaCy, NLTK
Generative AI: OpenAI API (GPT-3.5-turbo)
Translation: MarianMT (Helsinki-NLP) for English-Hindi
Intent Model: Keras/TensorFlow
Frontend: HTML, CSS, JavaScript

How It Works:
1. User sends a message via the web UI.
2. Language Detection: spaCy detects the language (English/Hindi).
3. Translation: If Hindi, message is translated to English for processing.
4. Sentiment & Topic Analysis: Hugging Face models analyze the message.
5. Generative Response: OpenAI API generates a context-aware reply.
6. Translation Back: If Hindi, reply is translated back to Hindi.
7. Intent Fallback: If generative response fails, intent-based fallback is used.
8. Reply is sent to the user.

Setup Instructions:
Tested on Windows and Linux with Python 3.8.


Step 1: Obtain the Project Files
Download or copy the project files to your working directory and navigate to the project folder.

Step 2: Create and Activate Virtual Environment
Create a virtual environment and activate it:
python -m venv venv
On Linux: source venv/bin/activate
On Windows: .\venv\Scripts\activate.bat

Step 3: Install Requirements
Install all required dependencies:
pip install -r requirements.txt

Step 4: Configure OpenAI API Key
Get your OpenAI API key from https://platform.openai.com/api-keys and set it as an environment variable:
On Linux/Mac: export OPENAI_API_KEY="your-api-key-here"
On Windows: set OPENAI_API_KEY=your-api-key-here
Alternatively, create a .env file in the project directory:
echo "OPENAI_API_KEY=your-api-key-here" > .env

Step 5: Download spaCy Model
Download the required spaCy model:
python -m spacy download en_core_web_sm

Step 6: Run the Application
Start the chatbot server:
python app.py

Step 7: Access the Chatbot
Open your browser and go to http://localhost:5000

Technical Details:
Requirements: All dependencies are listed in requirements.txt.
Model Downloads: On first run, large models (Hugging Face, MarianMT) will be downloaded automatically. Ensure you have at least 2GB free disk space and a stable internet connection.
OpenAI API: The chatbot uses OpenAI API for generative responses. You must provide a valid API key by setting the OPENAI_API_KEY environment variable.
Intent Model: The intent classifier uses pre-trained files: model.h5, texts.pkl, labels.pkl.
NLTK Data: NLTK will download required data automatically on first run.

Extending for Healthcare:
- Add healthcare-specific intents to intents.json.
- Integrate external health APIs for symptom checking, appointment booking, etc.
- Customize topic labels for medical domains.

Troubleshooting:
Model Download Slow/Stuck: Check your internet connection and disk space. Large models may take several minutes.
Import Errors: Ensure you are using Python 3.8 and have activated your virtual environment.
API Errors: Verify your OpenAI API key is set correctly as an environment variable (OPENAI_API_KEY).

Submission Report:
This document provides a comprehensive overview, setup guide, technical details, and extension instructions for the Mental Health Conversational AI Chatbot. All steps, dependencies, and architecture are explained for easy reproduction and evaluation.

For further questions or customization, contact the project maintainer or submit an issue on GitHub.
