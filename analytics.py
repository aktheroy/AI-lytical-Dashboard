import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Wedge, Arc

class DataAnalyzer:
    def __init__(self):
        self.df = self._load_data()
        self.style = {
            'font_color': 'white',
            'bg_color': '#ff6b6bb9',
            'colors': ['#ff6b6b', '#4caf4f', '#45b7d1', '#96ceb4', '#ffefad', '#691b9a', '#ff5622']
        }

    def _load_data(self):
        df = pd.read_csv('Data/cleaned_hotel_bookings.csv')
        df['revenue'] = df['adr'] * (df['stays_in_weekend_nights'] + df['stays_in_week_nights'])
        return df

    def _configure_plot(self, fig, ax):
        fig.patch.set_alpha(0)
        ax.set_facecolor(self.style['bg_color'])
        for spine in ax.spines.values():
            spine.set_color(self.style['font_color'])
        ax.tick_params(colors=self.style['font_color'])
        ax.xaxis.label.set_color(self.style['font_color'])
        ax.yaxis.label.set_color(self.style['font_color'])

    def generate_revenue_trend(self):
        df_grouped = self.df.groupby('arrival_date', as_index=False)['revenue'].sum()
        fig, ax = plt.subplots(figsize=(20, 3))
        self._configure_plot(fig, ax)
        
        sns.lineplot(data=df_grouped, x='arrival_date', y='revenue', 
                    color='white', linewidth=2.5, ax=ax)
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        return fig

    def generate_cancellation_rate(self):
        cancellation_rate = (self.df['is_canceled'].sum() / len(self.df)) * 100
        fig = plt.figure(figsize=(8, 4), facecolor='none')
        ax = fig.add_subplot(111, aspect='equal')
        
        # Gauge elements
        ax.add_patch(Arc((0.5, 0.5), 0.6, 0.6, theta1=0, theta2=180, color='lightgray', lw=20))
        ax.add_patch(Wedge((0.5, 0.5), 0.3, 0.6, 180*cancellation_rate/100, width=0.05, color=self.style['colors'][0]))
        plt.text(0.5, 0.5, f'{cancellation_rate:.1f}%', ha='center', va='center', fontsize=24, color='white')
        ax.axis('off')
        return fig, cancellation_rate

    def generate_geo_distribution(self):
        country_counts = self.df['country'].value_counts().nlargest(5)
        fig, ax = plt.subplots(figsize=(8, 3))
        self._configure_plot(fig, ax)

        # Create vertical bar chart
        bars = ax.bar(
        country_counts.index,  # X-axis: Country codes
        country_counts.values,  # Y-axis: Booking counts
        color=self.style['colors'][:5]  # Use first 5 colors from palette
    )
        
        # Customize the chart
        ax.set_xlabel('Country', color=self.style['font_color'])
        ax.set_ylabel('Number of Bookings', color=self.style['font_color'])

        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
            bar.get_x() + bar.get_width() / 2,  # X position (center of bar)
            height + 50,  # Y position (slightly above bar)
            f'{height:,}',  # Formatted number
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            color=self.style['font_color'],
            fontsize=12
        )
            
        # Remove unnecessary spines and legend
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend().remove()  # Remove legend
        
        return fig, country_counts.index.tolist()

    def generate_analytics(self):
        return {
            'revenue_fig': self.generate_revenue_trend(),
            'gauge_fig': self.generate_cancellation_rate()[0],
            'country_fig': self.generate_geo_distribution()[0],
            'cancellation_rate': self.generate_cancellation_rate()[1],
            'countries': self.generate_geo_distribution()[1]
        }