"""
Interactive Dashboard Generator

Creates a comprehensive, professional HTML dashboard for house price predictions.
Includes all key metrics, visualizations, and analytics.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os

# Configuration
DATA_DIR = "data/outputs"
PREDICTIONS_FILE = os.path.join(DATA_DIR, "predictions.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "predictions_summary.csv")
MODEL_COMP_FILE = os.path.join(DATA_DIR, "model_comparison.csv")
OUTPUT_FILE = "dashboard.html"

# Location mapping
LOCATION_MAP = {
    0: 'Ahmedabad',
    1: 'Bangalore',
    2: 'Chennai',
    3: 'Delhi',
    4: 'Hyderabad',
    5: 'Kolkata',
    6: 'Mumbai',
    7: 'Pune'
}

def load_data():
    """Load all prediction data."""
    df_pred = pd.read_csv(PREDICTIONS_FILE)
    df_summary = pd.read_csv(SUMMARY_FILE)
    df_models = pd.read_csv(MODEL_COMP_FILE)
    
    # Map location codes to names
    df_pred['location_name'] = df_pred['location'].map(LOCATION_MAP)
    df_summary['location_name'] = df_summary['location'].map(LOCATION_MAP)
    
    return df_pred, df_summary, df_models

def create_kpi_cards(df_pred):
    """Create KPI card data."""
    total_predictions = len(df_pred)
    accuracy_rate = (df_pred['within_10pct'].sum() / len(df_pred) * 100)
    avg_error_pct = df_pred['percentage_error'].mean()
    avg_error_rs = df_pred['absolute_error'].mean()
    
    return {
        'total_predictions': total_predictions,
        'accuracy_rate': accuracy_rate,
        'avg_error_pct': avg_error_pct,
        'avg_error_rs': avg_error_rs
    }

def create_scatter_chart(df_pred):
    """Actual vs Predicted Price scatter plot."""
    fig = px.scatter(
        df_pred,
        x='actual_price',
        y='predicted_price',
        color='within_10pct',
        hover_data=['property_id', 'location_name', 'bedrooms', 'percentage_error'],
        color_discrete_map={0: '#EF553B', 1: '#00CC96'},
        labels={
            'actual_price': 'Actual Price (Rs)',
            'predicted_price': 'Predicted Price (Rs)',
            'within_10pct': 'Within 10%'
        },
        title='Actual vs Predicted Price'
    )
    
    # Add diagonal line (perfect prediction)
    min_price = min(df_pred['actual_price'].min(), df_pred['predicted_price'].min())
    max_price = max(df_pred['actual_price'].max(), df_pred['predicted_price'].max())
    fig.add_trace(go.Scatter(
        x=[min_price, max_price],
        y=[min_price, max_price],
        mode='lines',
        name='Perfect Prediction',
        line=dict(dash='dash', color='gray')
    ))
    
    fig.update_layout(
        hovermode='closest',
        height=500,
        template='plotly_white'
    )
    return fig

def create_accuracy_by_location(df_summary):
    """Accuracy rate by location."""
    df_location = df_summary.groupby('location_name')['within_10pct_mean'].mean() * 100
    
    fig = px.bar(
        x=df_location.index,
        y=df_location.values,
        labels={'x': 'Location', 'y': 'Accuracy Rate (%)'},
        title='Prediction Accuracy by Location',
        color=df_location.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    return fig

def create_error_distribution(df_pred):
    """Error percentage distribution histogram."""
    fig = px.histogram(
        df_pred,
        x='percentage_error',
        nbins=30,
        title='Error Distribution',
        labels={'percentage_error': 'Percentage Error (%)', 'count': 'Number of Predictions'},
        color_discrete_sequence=['#636EFA']
    )
    
    # Add mean line
    mean_error = df_pred['percentage_error'].mean()
    fig.add_vline(x=mean_error, line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {mean_error:.2f}%")
    
    fig.update_layout(
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    return fig

def create_price_band_analysis(df_summary):
    """Error by price band."""
    df_band = df_summary.groupby('price_band').agg({
        'percentage_error_mean': 'mean',
        'property_id_count': 'sum',
        'within_10pct_mean': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Avg Error by Price Band", "Count by Price Band")
    )
    
    fig.add_trace(
        go.Bar(
            x=df_band['price_band'],
            y=df_band['percentage_error_mean'],
            name='Avg Error %',
            marker_color='#EF553B'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_band['price_band'],
            y=df_band['property_id_count'],
            name='Count',
            marker_color='#00CC96'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Price Band", row=1, col=1)
    fig.update_xaxes(title_text="Price Band", row=1, col=2)
    fig.update_yaxes(title_text="Error %", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    fig.update_layout(
        title_text="Analysis by Price Band",
        height=400,
        template='plotly_white',
        showlegend=False
    )
    return fig

def create_model_comparison(df_models):
    """Model performance comparison."""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("R² Score", "MAE (Rs)", "RMSE (Rs)")
    )
    
    colors = ['#636EFA', '#EF553B', '#00CC96']
    
    fig.add_trace(
        go.Bar(x=df_models['model_name'], y=df_models['r2'], 
               marker_color=colors, name='R² Score'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df_models['model_name'], y=df_models['mae'],
               marker_color=colors, name='MAE'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=df_models['model_name'], y=df_models['rmse'],
               marker_color=colors, name='RMSE'),
        row=1, col=3
    )
    
    fig.update_yaxes(title_text="Score", row=1, col=1)
    fig.update_yaxes(title_text="Rs", row=1, col=2)
    fig.update_yaxes(title_text="Rs", row=1, col=3)
    
    fig.update_layout(
        title_text="Model Performance Comparison",
        height=450,
        template='plotly_white',
        showlegend=False
    )
    return fig

def create_bedrooms_analysis(df_pred):
    """Average error by number of bedrooms."""
    df_bed = df_pred.groupby('bedrooms').agg({
        'percentage_error': 'mean',
        'property_id': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_bed['bedrooms'],
        y=df_bed['percentage_error'],
        mode='lines+markers',
        name='Avg Error',
        line=dict(color='#636EFA', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Prediction Error by Number of Bedrooms',
        xaxis_title='Number of Bedrooms',
        yaxis_title='Average Error (%)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    return fig

def create_html_dashboard(df_pred, df_summary, df_models, kpis):
    """Create complete HTML dashboard."""
    
    # Create all charts
    scatter = create_scatter_chart(df_pred)
    accuracy_loc = create_accuracy_by_location(df_summary)
    error_dist = create_error_distribution(df_pred)
    price_band = create_price_band_analysis(df_summary)
    model_comp = create_model_comparison(df_models)
    bedrooms = create_bedrooms_analysis(df_pred)
    
    # Convert to HTML
    scatter_html = scatter.to_html(include_plotlyjs=False, div_id="scatter")
    accuracy_html = accuracy_loc.to_html(include_plotlyjs=False, div_id="accuracy")
    error_html = error_dist.to_html(include_plotlyjs=False, div_id="error")
    price_html = price_band.to_html(include_plotlyjs=False, div_id="price")
    model_html = model_comp.to_html(include_plotlyjs=False, div_id="model")
    bedrooms_html = bedrooms.to_html(include_plotlyjs=False, div_id="bedrooms")
    
    # Create HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>House Price Prediction Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            header {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            header h1 {{
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            header p {{
                color: #666;
                font-size: 1.1em;
            }}
            
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .kpi-card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #667eea;
                transition: transform 0.3s ease;
            }}
            
            .kpi-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
            }}
            
            .kpi-card.blue {{
                border-left-color: #667eea;
            }}
            
            .kpi-card.green {{
                border-left-color: #00CC96;
            }}
            
            .kpi-card.orange {{
                border-left-color: #FFA500;
            }}
            
            .kpi-card.red {{
                border-left-color: #EF553B;
            }}
            
            .kpi-label {{
                color: #999;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
            }}
            
            .kpi-value {{
                font-size: 2em;
                font-weight: bold;
                color: #333;
            }}
            
            .kpi-subtitle {{
                color: #666;
                font-size: 0.85em;
                margin-top: 8px;
            }}
            
            .chart-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .chart-full {{
                grid-column: 1 / -1;
            }}
            
            footer {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: #666;
                margin-top: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .metric-box {{
                display: inline-block;
                margin: 0 20px;
            }}
            
            .metric-label {{
                color: #999;
                font-size: 0.9em;
            }}
            
            .metric-value {{
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
            }}
            
            @media (max-width: 768px) {{
                .chart-grid {{
                    grid-template-columns: 1fr;
                }}
                
                header h1 {{
                    font-size: 1.8em;
                }}
                
                .kpi-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🏠 House Price Prediction Dashboard</h1>
                <p>Real-time analytics and model performance metrics</p>
            </header>
            
            <div class="kpi-grid">
                <div class="kpi-card blue">
                    <div class="kpi-label">Total Predictions</div>
                    <div class="kpi-value">{kpis['total_predictions']:,}</div>
                    <div class="kpi-subtitle">Test set properties analyzed</div>
                </div>
                
                <div class="kpi-card green">
                    <div class="kpi-label">Accuracy Rate</div>
                    <div class="kpi-value">{kpis['accuracy_rate']:.1f}%</div>
                    <div class="kpi-subtitle">Within ±10% error margin</div>
                </div>
                
                <div class="kpi-card orange">
                    <div class="kpi-label">Avg Error %</div>
                    <div class="kpi-value">{kpis['avg_error_pct']:.2f}%</div>
                    <div class="kpi-subtitle">Mean percentage error</div>
                </div>
                
                <div class="kpi-card red">
                    <div class="kpi-label">Avg Error Amount</div>
                    <div class="kpi-value">Rs {kpis['avg_error_rs']:,.0f}</div>
                    <div class="kpi-subtitle">Mean absolute error</div>
                </div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-container chart-full">
                    {scatter_html}
                </div>
                
                <div class="chart-container">
                    {accuracy_html}
                </div>
                
                <div class="chart-container">
                    {error_html}
                </div>
                
                <div class="chart-container chart-full">
                    {price_html}
                </div>
                
                <div class="chart-container chart-full">
                    {model_html}
                </div>
                
                <div class="chart-container">
                    {bedrooms_html}
                </div>
            </div>
            
            <footer>
                <div class="metric-box">
                    <div class="metric-label">Best Model</div>
                    <div class="metric-value">Random Forest Regressor</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">R² Score</div>
                    <div class="metric-value">0.9984</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Features</div>
                    <div class="metric-value">13</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Training Samples</div>
                    <div class="metric-value">3,904</div>
                </div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                <p>Dashboard generated on 2026-04-28 | Data from House Price Prediction Model</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Generate dashboard."""
    print("Loading data...")
    df_pred, df_summary, df_models = load_data()
    
    print("Calculating KPIs...")
    kpis = create_kpi_cards(df_pred)
    
    print("Creating dashboard...")
    html_content = create_html_dashboard(df_pred, df_summary, df_models, kpis)
    
    print(f"Saving dashboard to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Dashboard created successfully!")
    print(f"✓ Open this file in your browser: {os.path.abspath(OUTPUT_FILE)}")
    print(f"\nDashboard includes:")
    print(f"  • 4 Key Performance Indicator cards")
    print(f"  • Actual vs Predicted Price scatter plot")
    print(f"  • Accuracy by location analysis")
    print(f"  • Error distribution histogram")
    print(f"  • Analysis by price band")
    print(f"  • Model performance comparison")
    print(f"  • Error analysis by bedrooms")

if __name__ == '__main__':
    main()
