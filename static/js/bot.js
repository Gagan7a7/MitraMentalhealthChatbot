// Clock functionality
function updateTime() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = now.getMinutes();
    var seconds = now.getSeconds();
    
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    
    var timeString = hours + ':' + minutes;
    document.getElementById('clock').textContent = timeString;
}

setInterval(updateTime, 1000);

// Chatbot toggle functionality
document.getElementById("chatbot_toggle").onclick = function () {
    var chatbot = document.getElementById("chatbot");
    var toggleBtn = document.getElementById("chatbot_toggle");
    var openIcon = toggleBtn.children[0];
    var closeIcon = toggleBtn.children[1];
    
    if (chatbot.classList.contains("collapsed")) {
        chatbot.classList.remove("collapsed");
        openIcon.style.display = "none";
        closeIcon.style.display = "inline";
    } else {
        chatbot.classList.add("collapsed");
        openIcon.style.display = "inline";
        closeIcon.style.display = "none";
    }
};

// Chat functionality
const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

// Bot and user configurations
const BOT_IMG = "static/img/mhcicon.png";
const PERSON_IMG = "static/img/person.png";
const BOT_NAME = "mitra";
const PERSON_NAME = "You";

// Conversation context tracking
let conversationContext = {
    messageCount: 0,
    lastTopic: null,
    userMood: 'neutral',
    crisisDetected: false
};

// Handle form submission
msgerForm.addEventListener("submit", event => {
    event.preventDefault();
    
    const msgText = msgerInput.value.trim();
    if (!msgText) return;
    
    // Update conversation context
    conversationContext.messageCount++;
    
    // Add user message to chat
    appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
    msgerInput.value = "";
    
    // Show typing indicator with more natural delay
    showTypingIndicator();
    
    // Add slight delay for more natural feel
    setTimeout(() => {
        botResponse(msgText);
    }, 800 + Math.random() * 1200); // Random delay between 0.8-2 seconds
});

// Enhanced message appending with better formatting
function appendMessage(name, img, side, text) {
    // Detect crisis responses
    const isCrisis = text.toLowerCase().includes('988') || 
                    text.toLowerCase().includes('crisis') ||
                    text.toLowerCase().includes('suicide');
    
    // Detect different types of responses for styling
    const isEncouraging = /\b(proud|great job|well done|good work|you can|you're strong|you've got this)\b/i.test(text);
    const isEmpathetic = /\b(sorry|understand|hear you|tough time|difficult|struggling)\b/i.test(text);
    
    let messageClass = '';
    let iconEmoji = '';
    
    if (side === 'left') { // Bot messages
        if (isCrisis) {
            messageClass = 'crisis-message';
            iconEmoji = '🆘';
        } else if (isEncouraging) {
            messageClass = 'encouraging-message';
            iconEmoji = '💪';
        } else if (isEmpathetic) {
            messageClass = 'empathetic-message';
            iconEmoji = '🤗';
        }
    }
    
    const msgHTML = `
        <div class="msg ${side}-msg ${messageClass}">
            <div class="msg-img" style="background-image: url(${img})"></div>
            <div class="msg-bubble">
                <div class="msg-info">
                    <div class="msg-info-name">${name} ${iconEmoji}</div>
                    <div class="msg-info-time">${formatDate(new Date())}</div>
                </div>
                <div class="msg-text">${text}</div>
            </div>
        </div>
    `;
    
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
    
    // Show follow-up suggestions for certain types of responses
    if (side === 'left' && conversationContext.messageCount > 1) {
        setTimeout(() => {
            showContextualSuggestions(text);
        }, 2000);
    }
}

// Enhanced typing indicator
function showTypingIndicator() {
    const encouragingMessages = [
        "Mitra is thinking...",
        "Mitra is here for you...",
        "Processing your message with care...",
        "Mitra is listening..."
    ];
    
    const randomMessage = encouragingMessages[Math.floor(Math.random() * encouragingMessages.length)];
    
    const typingHTML = `
        <div class="msg left-msg typing-indicator">
            <div class="msg-img" style="background-image: url(${BOT_IMG})"></div>
            <div class="msg-bubble">
                <div class="msg-info">
                    <div class="msg-info-name">${randomMessage}</div>
                </div>
                <div class="msg-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    msgerChat.insertAdjacentHTML("beforeend", typingHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Enhanced bot response with better error handling
function botResponse(rawText) {
    $.get("/get", { msg: rawText })
        .done(function (data) {
            removeTypingIndicator();
            let msgText = data.toString().trim();
            
            // Clean formatting but preserve empathetic language
            msgText = msgText.replace(/\*\*/g, '');
            msgText = msgText.replace(/\*/g, '');
            msgText = msgText.replace(/#{1,6}\s?/g, '');
            msgText = msgText.replace(/```[\s\S]*?```/g, '');
            msgText = msgText.replace(/`([^`]*)`/g, '$1');
            msgText = msgText.replace(/\[\d+\]/g, '');
            msgText = msgText.replace(/Loading bot response[\.]*/, '');
            msgText = msgText.replace(/Perplexity API/, '');
            msgText = msgText.replace(/\s+/g, ' ').trim();
            
            // Fallback for empty responses
            if (!msgText || msgText.length < 3) {
                msgText = "I'm here to listen and support you. What's been on your mind lately?";
            }
            
            // Update conversation context based on response
            updateConversationContext(rawText, msgText);
            
            appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
            
            // Show action buttons for specific scenarios
            showActionButtons(msgText);
        })
        .fail(function(xhr, status, error) {
            removeTypingIndicator();
            console.log("Error:", error);
            
            const supportiveErrors = [
                "I'm having a technical moment, but I'm still here for you. How are you feeling?",
                "Something went wrong on my end, but that doesn't change that I care about you. What's on your mind?",
                "Technical hiccup! But I'm still here to listen. Want to try telling me again?",
                "My circuits got a bit tangled, but my support for you is unwavering. How can I help?"
            ];
            
            const randomError = supportiveErrors[Math.floor(Math.random() * supportiveErrors.length)];
            appendMessage(BOT_NAME, BOT_IMG, "left", randomError);
        });
}

// Update conversation context
function updateConversationContext(userInput, botResponse) {
    // Detect mood from user input
    const userLower = userInput.toLowerCase();
    if (userLower.includes('sad') || userLower.includes('depressed') || userLower.includes('down')) {
        conversationContext.userMood = 'sad';
    } else if (userLower.includes('anxious') || userLower.includes('worried') || userLower.includes('stressed')) {
        conversationContext.userMood = 'anxious';
    } else if (userLower.includes('angry') || userLower.includes('frustrated') || userLower.includes('mad')) {
        conversationContext.userMood = 'angry';
    } else if (userLower.includes('happy') || userLower.includes('good') || userLower.includes('better')) {
        conversationContext.userMood = 'positive';
    }
    
    // Detect crisis
    if (botResponse.includes('988') || botResponse.includes('crisis')) {
        conversationContext.crisisDetected = true;
    }
}

// Show contextual suggestions based on conversation
function showContextualSuggestions(botResponse) {
    // Remove any existing suggestions
    const existingSuggestions = document.querySelector('.contextual-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    let suggestions = [];
    
    // Context-aware suggestions
    if (botResponse.toLowerCase().includes('breathing') || botResponse.toLowerCase().includes('anxiety')) {
        suggestions = [
            "Can you guide me through a breathing exercise?",
            "I'd like to try a calming technique",
            "What other ways can help with anxiety?"
        ];
    } else if (botResponse.toLowerCase().includes('depression') || botResponse.toLowerCase().includes('sad')) {
        suggestions = [
            "How can I feel less alone?",
            "What helps when everything feels hopeless?",
            "I want to talk more about this"
        ];
    } else if (botResponse.toLowerCase().includes('stress') || botResponse.toLowerCase().includes('overwhelmed')) {
        suggestions = [
            "How can I manage my workload better?",
            "I need help prioritizing things",
            "What are some quick stress relief tips?"
        ];
    } else if (conversationContext.messageCount > 3 && Math.random() > 0.7) {
        // General supportive suggestions after a few exchanges
        suggestions = [
            "I'd like to talk about something else",
            "Can you help me think of positive things?",
            "What should I do when I feel like this again?"
        ];
    }
    
    if (suggestions.length > 0) {
        const suggestionsHTML = suggestions.map(suggestion => 
            `<button class="suggestion-btn" onclick="sendQuickResponse('${suggestion}')">${suggestion}</button>`
        ).join('');
        
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'contextual-suggestions';
        suggestionsContainer.innerHTML = `
            <div class="suggestions-title">💭 You might want to ask:</div>
            <div class="suggestions-buttons">${suggestionsHTML}</div>
        `;
        
        msgerChat.appendChild(suggestionsContainer);
        msgerChat.scrollTop = msgerChat.scrollHeight;
        
        // Auto-remove suggestions after 30 seconds
        setTimeout(() => {
            if (suggestionsContainer.parentNode) {
                suggestionsContainer.remove();
            }
        }, 30000);
    }
}

// Show actionable follow-up buttons for specific responses
function showActionButtons(botResponseText) {
    let actions = [];
    const responseLower = botResponseText.toLowerCase();
    
    if (responseLower.includes('crisis') || responseLower.includes('988')) {
        actions = [
            { label: "I need immediate help", text: "I'm in crisis and need help right now", priority: "high" },
            { label: "I'm feeling a bit better", text: "I'm feeling a bit safer now but still need support" }
        ];
    } else if (responseLower.includes('breathing') || responseLower.includes('calm')) {
        actions = [
            { label: "Guide me through breathing", text: "Can you walk me through a breathing exercise step by step?" },
            { label: "Other calming techniques", text: "What are some other ways to calm down when I'm anxious?" }
        ];
    } else if (responseLower.includes('professional help') || responseLower.includes('counselor')) {
        actions = [
            { label: "How do I find help?", text: "How do I find a mental health professional?" },
            { label: "What should I expect?", text: "What should I expect from therapy or counseling?" }
        ];
    } else if (responseLower.includes('study') || responseLower.includes('exam') || responseLower.includes('academic')) {
        actions = [
            { label: "Study stress tips", text: "Can you give me tips for managing study stress?" },
            { label: "Time management help", text: "I need help managing my time better" }
        ];
    }
    
    if (actions.length > 0) {
        const btns = actions.map(action => {
            const priorityClass = action.priority === 'high' ? 'high-priority-btn' : '';
            return `<button class='action-btn ${priorityClass}' onclick="sendQuickResponse('${action.text}')">${action.label}</button>`;
        }).join('');
        
        const container = document.createElement('div');
        container.className = 'action-buttons-container';
        container.innerHTML = `
            <div class="action-buttons-title">🎯 Quick actions:</div>
            <div class="action-buttons">${btns}</div>
        `;
        
        msgerChat.appendChild(container);
        msgerChat.scrollTop = msgerChat.scrollHeight;
        
        // Remove action buttons after being used or after 45 seconds
        setTimeout(() => {
            if (container.parentNode) {
                container.remove();
            }
        }, 45000);
    }
}

// Utility functions
function get(selector, root = document) {
    return root.querySelector(selector);
}

function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();
    return `${h.slice(-2)}:${m.slice(-2)}`;
}

// Enhanced quick responses based on mental health focus
function addInitialQuickResponses() {
    const quickResponses = [
        "How are you doing today?",
        "I'm feeling stressed about school",
        "I've been feeling anxious lately",
        "I'm having trouble sleeping",
        "I feel overwhelmed with everything",
        "I need someone to talk to"
    ];
    
    const quickResponsesHTML = quickResponses.map(response => 
        `<button class="quick-response-btn" onclick="sendQuickResponse('${response}')">${response}</button>`
    ).join('');
    
    const quickResponsesContainer = document.createElement('div');
    quickResponsesContainer.className = 'initial-quick-responses';
    quickResponsesContainer.innerHTML = `
        <div class="welcome-message">
            <h3>👋 Hi there! I'm Mitra, your mental health support companion.</h3>
            <p>I'm here to listen, support, and help you through whatever you're facing. Pick a topic below or just start typing:</p>
        </div>
        <div class="quick-responses-title">✨ Start with:</div>
        <div class="quick-responses-grid">${quickResponsesHTML}</div>
    `;
    
    msgerChat.appendChild(quickResponsesContainer);
}

function sendQuickResponse(text) {
    // Remove initial quick responses after first interaction
    const initialResponses = document.querySelector('.initial-quick-responses');
    if (initialResponses) {
        initialResponses.remove();
    }
    
    // Remove any contextual suggestions
    const suggestions = document.querySelector('.contextual-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
    
    // Remove action buttons
    const actionButtons = document.querySelector('.action-buttons-container');
    if (actionButtons) {
        actionButtons.remove();
    }
    
    // Send the message
    appendMessage(PERSON_NAME, PERSON_IMG, "right", text);
    showTypingIndicator();
    
    setTimeout(() => {
        botResponse(text);
    }, 1000 + Math.random() * 1000);
}

// Add some encouraging animations and effects
function addEncouragingEffects() {
    // Add subtle animations to messages
    const style = document.createElement('style');
    style.textContent = `
        .msg {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .crisis-message .msg-bubble {
            border-left: 4px solid #ff4757;
            background-color: #fff5f5;
        }
        
        .encouraging-message .msg-bubble {
            border-left: 4px solid #2ecc71;
            background-color: #f0fff4;
        }
        
        .empathetic-message .msg-bubble {
            border-left: 4px solid #3498db;
            background-color: #f0f8ff;
        }
        
        .suggestion-btn, .action-btn, .quick-response-btn {
            margin: 4px;
            padding: 8px 12px;
            border: 2px solid #3498db;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-size: 14px;
        }
        
        .suggestion-btn:hover, .action-btn:hover, .quick-response-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .high-priority-btn {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
        }
        
        .contextual-suggestions, .action-buttons-container, .initial-quick-responses {
            margin: 10px 0;
            padding: 15px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .suggestions-title, .action-buttons-title, .quick-responses-title {
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .welcome-message {
            text-align: center;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .welcome-message h3 {
            margin: 0 0 10px 0;
            color: #3498db;
        }
        
        .welcome-message p {
            margin: 0;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .quick-responses-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
        }
        
        .typing-dots span {
            animation: typingAnimation 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: 0s; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typingAnimation {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
    `;
    document.head.appendChild(style);
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add initial quick responses only if chat is empty
    if (msgerChat.children.length === 0) {
        addInitialQuickResponses();
    }
    
    // Add encouraging effects
    addEncouragingEffects();
    
    // Focus on input for better UX
    msgerInput.focus();
    
    // Add enter key support for better accessibility
    msgerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            msgerForm.dispatchEvent(new Event('submit'));
        }
    });
    
    console.log('🤖 Enhanced Mental Health Chatbot UI loaded successfully!');
    console.log('💚 Ready to support student wellbeing!');
});
