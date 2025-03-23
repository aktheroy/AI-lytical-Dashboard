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

function createRoomMealLegend() {
    const colors = ['#ff6b6b', '#4caf4f', '#45b7d1', '#96ceb4', '#ffefad', '#691b9a', '#ff5622'];  // Match pie chart colors
    const rooms = JSON.parse(document.getElementById('room-data').textContent);
    const meals = JSON.parse(document.getElementById('meal-data').textContent);
    const legend = document.getElementById('room-meal-legend');
    
    // Add room types
    legend.innerHTML = '<h4>Room Types</h4>';
    rooms.forEach((room, index) => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${colors[index]}"></div>
            <span>${room}</span>
        `;
        legend.appendChild(item);
    });
    
    // Add meal types
    legend.innerHTML += '<h4>Meal Types</h4>';
    meals.forEach((meal, index) => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${colors[rooms.length + index]}"></div>
            <span>${meal}</span>
        `;
        legend.appendChild(item);
    });
}

