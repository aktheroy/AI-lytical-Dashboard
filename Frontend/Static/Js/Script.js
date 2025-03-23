document.addEventListener('DOMContentLoaded', () => {
    initializeDate();
    initializeChat();
});

function initializeDate() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', options);
}

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

        chatMessages.appendChild(createMessageElement(message));
        setTimeout(() => {
            chatMessages.appendChild(createMessageElement('Thank you for your message! Our team will respond shortly.', false));
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);
        input.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    sendBtn.addEventListener('click', handleSendMessage);
    input.addEventListener('keypress', (e) => e.key === 'Enter' && handleSendMessage());
}

