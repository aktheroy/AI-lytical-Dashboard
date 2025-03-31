// script.js
async function fetchAnalytics() {
    try {
        console.log('Fetching analytics data...');
        const response = await fetch('/analytics');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        
        // Update all charts
        const charts = [
            ['revenue-chart', data.revenue_plot],
            ['gauge-chart', data.gauge_plot],
            ['country-chart', data.country_plot],
            ['customer-seg-chart', data.customer_seg_fig],
            ['lead-time-chart', data.lead_time_fig],
            ['room-meal-chart', data.room_meal_fig]
        ];
        
        charts.forEach(([id, b64]) => {
            const img = document.getElementById(id);
            if (img) img.src = `data:image/png;base64,${b64}`;
        });

        // Update cancellation rate
        const gaugeLabel = document.querySelector('.gauge-label');
        if (gaugeLabel) gaugeLabel.textContent = data.cancellation_rate;

    } catch (error) {
        console.error('Error fetching analytics:', error);
    }
}

function sanitizeInput(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const sendBtn = document.querySelector('.send-btn');
    const chatMessages = document.querySelector('.chat-messages');
    const message = input.value.trim();

    if (!message) return;

    try {
        // Add user message
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user';
        userMessageDiv.innerHTML = `<p>${sanitizeInput(message)}</p>`;
        chatMessages.appendChild(userMessageDiv);
        userMessageDiv.classList.add('visible');

        // Clear input
        input.value = '';
        
        // Add loading indicator
        const loadingMessageDiv = document.createElement('div');
        loadingMessageDiv.className = 'message bot loading';
        loadingMessageDiv.innerHTML = '<p class="loading-dots">Thinking</p>';
        chatMessages.appendChild(loadingMessageDiv);
        loadingMessageDiv.classList.add('visible');

        // Get bot response
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) throw new Error('Bot response failed');
        const data = await response.json();

        // Remove loading message
        chatMessages.removeChild(loadingMessageDiv);

        // Add bot response
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot';
        botMessageDiv.innerHTML = `<p>${sanitizeInput(data.response)}</p>`;
        chatMessages.appendChild(botMessageDiv);
        botMessageDiv.classList.add('visible');

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        console.error('Chat error:', error);
        // Remove loading message if present
        const loadingMessages = document.querySelectorAll('.loading');
        loadingMessages.forEach(msg => msg.remove());

        // Add error message
        const errorMessageDiv = document.createElement('div');
        errorMessageDiv.className = 'message bot error';
        errorMessageDiv.innerHTML = '<p>Sorry, I\'m having trouble responding. Please try again.</p>';
        chatMessages.appendChild(errorMessageDiv);
        errorMessageDiv.classList.add('visible');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function initializeChat() {
    const input = document.getElementById('message-input');
    const sendBtn = document.querySelector('.send-btn');
    const chatMessages = document.querySelector('.chat-messages');

    if (!input || !sendBtn || !chatMessages) {
        console.error('Chat elements not found!');
        return;
    }

    // Event listeners
    sendBtn.addEventListener('click', async () => {
        sendBtn.disabled = true;
        await sendMessage();
        sendBtn.disabled = false;
    });

    input.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.disabled = true;
            await sendMessage();
            sendBtn.disabled = false;
        }
    });
}

function initializeDate() {
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = new Date().toLocaleDateString('en-US', options);
    }
}

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
    initializeDate();
    initializeChat();
    fetchAnalytics();

    document.getElementById('analyze-btn')?.addEventListener('click', fetchAnalytics);
});