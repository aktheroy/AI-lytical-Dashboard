from flask import Flask, render_template,request,jsonify
import base64
from io import BytesIO
from analytics import DataAnalyzer
from RagLLMs import RAGLLM  # Import the RAGLLM class


app = Flask(__name__, template_folder='Frontend/Templates', static_folder='Frontend/Static')

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/analytics')
def analytics():
    analyzer = DataAnalyzer()
    results = analyzer.generate_analytics()
    
    return jsonify({
        'revenue_plot': fig_to_base64(results['revenue_fig']),
        'gauge_plot': fig_to_base64(results['gauge_fig']),
        'country_plot': fig_to_base64(results['country_fig']),
        'customer_seg_fig': fig_to_base64(results['customer_seg_fig']),
        'lead_time_fig': fig_to_base64(results['lead_time_fig']),
        'room_meal_fig': fig_to_base64(results['room_meal_fig']),
        'cancellation_rate': f"{results['cancellation_rate']:.1f}%",
        'countries': results['countries'],
        'segments': results['segments'],
        'rooms': results['rooms'],
        'meals': results['meals']
    })


@app.route('/ask', methods=['POST'])
def ask():
    rag_llm = RAGLLM()
    data = request.get_json()
    user_message = data.get('message', '')

    # Process the message using RAGLLM
    result = rag_llm.process_message(user_message)
    answer = result["response"]

    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run(debug=True)