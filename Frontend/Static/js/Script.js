// Date Initialization
function initializeDate() {
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    document.getElementById('current-date').textContent = 
        new Date().toLocaleDateString('en-US', options);
}

// Chat Functionality
function initializeChat() {
    const input = document.getElementById('message-input');
    const sendBtn = document.querySelector('.send-btn');
    const chatMessages = document.querySelector('.chat-messages');

    const createMessageElement = (text, isUser = true) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        return messageDiv;
    };

    const handleSendMessage = () => {
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        chatMessages.appendChild(createMessageElement(message));
        
        // Simulate bot response
        setTimeout(() => {
            chatMessages.appendChild(
                createMessageElement('Thank you for your message! Our team will respond shortly.', false)
            );
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);

        // Clear input
        input.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Event Listeners
    sendBtn.addEventListener('click', handleSendMessage);
    input.addEventListener('keypress', (e) => e.key === 'Enter' && handleSendMessage());
}

// Initialize all components
document.addEventListener('DOMContentLoaded', () => {
    initializeDate();
    initializeChat();
});

