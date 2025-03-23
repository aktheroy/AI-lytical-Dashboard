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

// Chat functionality
function initializeChat() {
    const input = document.getElementById('message-input');
    const sendBtn = document.querySelector('.send-btn');
    const chatMessages = document.querySelector('.chat-messages');

    // Debug: Check if elements exist
    console.log('Chat input:', input);
    console.log('Send button:', sendBtn);
    console.log('Chat messages container:', chatMessages);
    if (!input || !sendBtn || !chatMessages) {
        console.error('Chat elements not found!');
        return;
        }

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        console.log('Sending message:', message); // Debug: Log the message


        try {
            // Add user message
            chatMessages.innerHTML += `
                <div class="message user">
                    <p>${message}</p>
                </div>
            `;

            // Get bot response
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Add bot response
            chatMessages.innerHTML += `
                <div class="message bot">
                    <p>${data.response}</p>
                </div>
            `;

            // Clear input and scroll to bottom
            input.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Chat error:', error);
        }
    }

    // Add event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Debug: Verify listeners are attached
    console.log('Event listeners added for chat');

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
    fetchAnalytics();  // Initial load

    document.getElementById('analyze-btn')?.addEventListener('click', fetchAnalytics);
});