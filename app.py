from flask import Flask, render_template
import base64
from io import BytesIO
from analytics import DataAnalyzer

app = Flask(__name__, template_folder='Frontend/Templates', static_folder='Frontend/Static')

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

@app.route('/')
def home():
    analyzer = DataAnalyzer()
    results = analyzer.generate_analytics()
    
    return render_template('Home.html',
                         revenue_plot=fig_to_base64(results['revenue_fig']),
                         gauge_plot=fig_to_base64(results['gauge_fig']),
                         country_plot=fig_to_base64(results['country_fig']),
                         customer_seg_fig=fig_to_base64(results['customer_seg_fig']),
                         lead_time_fig=fig_to_base64(results['lead_time_fig']),
                         room_meal_fig=fig_to_base64(results['room_meal_fig']),  # New chart
                         cancellation_rate=f"{results['cancellation_rate']:.1f}%",
                         countries=results['countries'],
                         segments=results['segments'],
                         rooms=results['rooms'],  # Room labels
                         meals=results['meals'])  # Meal labels

if __name__ == '__main__':
    app.run(debug=True)