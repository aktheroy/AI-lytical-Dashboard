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
            'colors': [
                '#ff6b6b', '#4caf4f', '#45b7d1', '#96ceb4', '#ffefad', 
                '#691b9a', '#ff5622', '#8e44ad', '#3498db', '#2ecc71', 
                '#e67e22', '#e74c3c', '#1abc9c', '#9b59b6', '#34495e'
            ]
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
        fig, ax = plt.subplots(figsize=(26, 8))
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
        ax.add_patch(Wedge((0.5, 0.5), 0.3, 0.6, 180*cancellation_rate/100, width=0.09, color=self.style['colors'][0]))
        plt.text(0.5, 0.5, f'{cancellation_rate:.1f}%', ha='center', va='center', fontsize=24, color='white')
        ax.axis('off')
        return fig, cancellation_rate

    def generate_geo_distribution(self):
        country_counts = self.df['country'].value_counts().nlargest(5)
        fig, ax = plt.subplots(figsize=(12, 8))
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
        
        return fig, country_counts.index.tolist()

    def generate_customer_segmentation(self):
        # Get customer segmentation data
        segment_counts = self.df['customer_segment'].value_counts()
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 8))
        self._configure_plot(fig, ax)  # Apply consistent styling
        
        # Create donut pie chart
        wedges, texts, autotexts = ax.pie(
            segment_counts,
            labels=segment_counts.index,
            colors=self.style['colors'][:len(segment_counts)],  # Use colors from palette
            autopct='%1.2f%%',  # Show percentages
            startangle=60,  # Start from top
            wedgeprops=dict(width=1),
            explode= [0,0.2,0.2,0.4],  # Create donut hole
            textprops={'color': self.style['font_color'], 'fontsize': 30}
        )        
        # Make percentage text white and bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.4, fc='none')
        ax.add_artist(centre_circle)
        
        # Remove unnecessary spines
        ax.axis('equal')  # Ensure pie is circular
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend = 'labels'
        
        return fig, segment_counts.index.tolist()

    def generate_lead_time_distribution(self):
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(24, 8))
        self._configure_plot(fig, ax)  # Apply consistent styling
        
        # Create KDE plot
        sns.kdeplot(
            data=self.df,
            x='lead_time',  # Assuming 'lead_time' is the column name
            color=self.style['colors'][4],  # Use primary color
            fill=True,  # Fill under the curve
            alpha=0.5,  # Transparency
            ax=ax
        )
        
        # Customize the chart
        ax.set_xlabel('Lead Time (Days)', color=self.style['font_color'])
        ax.set_ylabel('Density', color=self.style['font_color'])
        
        # Remove unnecessary spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig

    def generate_room_meal_distribution(self):
        # Get data for room types and meals
        room_counts = self.df['reserved_room_type'].value_counts().nlargest(3)
        meal_counts = self.df['meal'].value_counts().nlargest(3)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 8))
        self._configure_plot(fig, ax)  # Apply consistent styling
        
        # Define colors for outer and inner pie charts
        colors = self.style['colors']
        
        # Outer pie: Room types
        wedges_outer, texts_outer, autotexts_outer = ax.pie(
            room_counts,
            labels=room_counts.index,
            colors=colors[:len(room_counts)],  # Use first N colors for room types
            radius=1.2,  # Outer radius
            startangle=30,  # Start from top
            wedgeprops=dict(width=0.4),  # Create donut hole
            autopct='%1.1f%%',  # Show percentages
            textprops={'color': self.style['font_color'], 'fontsize': 22}
        )
        
        # Inner pie: Meals
        wedges_inner, texts_inner, autotexts_inner = ax.pie(
            meal_counts,
            labels=meal_counts.index,
            colors=colors[len(room_counts):len(room_counts) + len(meal_counts)],  # Use next set of colors for meals
            radius=0.8,  # Inner radius
            startangle=90,  # Start from top
            wedgeprops=dict(width=0.4),  # Create donut hole
            autopct='%1.1f%%',  # Show percentages
            textprops={'color': self.style['font_color'], 'fontsize': 20}
        )        
        # Make percentage text white and bold
        for autotext in autotexts_outer + autotexts_inner:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.4, fc='none')
        ax.add_artist(centre_circle)
        
        # Remove unnecessary spines
        ax.axis('equal')  # Ensure pie is circular
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig, {
            'rooms': room_counts.index.tolist(),
            'meals': meal_counts.index.tolist()
        }

    def generate_analytics(self):
        return {
            'revenue_fig': self.generate_revenue_trend(),
            'gauge_fig': self.generate_cancellation_rate()[0],
            'country_fig': self.generate_geo_distribution()[0],
            'customer_seg_fig': self.generate_customer_segmentation()[0],
            'lead_time_fig': self.generate_lead_time_distribution(),
            'room_meal_fig': self.generate_room_meal_distribution()[0],  # New chart
            'cancellation_rate': self.generate_cancellation_rate()[1],
            'countries': self.generate_geo_distribution()[1],
            'segments': self.generate_customer_segmentation()[1],
            'rooms': self.generate_room_meal_distribution()[1]['rooms'],  # Room labels
            'meals': self.generate_room_meal_distribution()[1]['meals']  # Meal labels
        }