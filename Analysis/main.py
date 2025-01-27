import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="error_log.txt", level=logging.ERROR, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

class SalesData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File {self.file_path} does not exist.")
            self.data = pd.read_csv(self.file_path)
            # Convert 'Date' column to datetime format
            self.data['Date'] = pd.to_datetime(self.data['Date'])
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def clean_data(self):
        try:
            # Fill missing values with the average sales for respective region and product
            self.data['Sales'] = self.data.groupby(['Region', 'Product'])['Sales'].transform(lambda x: x.fillna(x.mean()))

            # Remove outliers (1.5 * IQR rule)
            q1 = self.data['Sales'].quantile(0.25)
            q3 = self.data['Sales'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            self.data = self.data[(self.data['Sales'] >= lower_bound) & (self.data['Sales'] <= upper_bound)]
        except Exception as e:
            logging.error(f"Error cleaning data: {e}")

    def save_data(self, output_file):
        try:
            self.data.to_csv(output_file, index=False)
        except Exception as e:
            logging.error(f"Error saving data: {e}")

class DataAnalyzer:
    def __init__(self, data):
        self.data = data

    def total_sales(self):
        return self.data.groupby('Region')['Sales'].sum()

    def top_product(self):
        return self.data.groupby(['Region', 'Product'])['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).groupby('Region').first()

    def average_sales(self):
        try:
            return self.data.groupby(['Region', pd.Grouper(key='Date', freq='ME')])['Sales'].mean()
        except Exception as e:
            logging.error(f"Error calculating average sales: {e}")


class Visualizer:
    @staticmethod
    def plot_bar(data, title):
        data.plot(kind='bar', color='skyblue', title=title)
        plt.xlabel('Region')
        plt.ylabel('Total Sales')
        plt.show()

    @staticmethod
    def plot_line(data, title):
        data.plot(kind='line', marker='o', title=title)
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.show()

    @staticmethod
    def plot_pie(data, title):
        data.plot(kind='pie', autopct='%1.1f%%', title=title)
        plt.ylabel('')
        plt.show()

    @staticmethod
    def plot_interactive(data, chart_type, title):
        if chart_type == 'scatter':
            fig = px.scatter(
                data, 
                x='Date', 
                y='Sales', 
                color='Region', 
                title=title,
                labels={'Sales': 'Sales Amount', 'Date': 'Date'}
            )
        elif chart_type == 'bar':
            fig = px.bar(
                data, 
                x='Product', 
                y='Sales', 
                color='Region', 
                title=title,
                labels={'Sales': 'Total Sales', 'Product': 'Product'}
            )
        elif chart_type == 'heatmap':
            fig = px.imshow(
                data, 
                labels=dict(color="Average Sales"),
                title=title,
                color_continuous_scale="Viridis"
            )
        
        # Add dropdowns for Region and Product filters
        if 'Region' in data.columns and 'Product' in data.columns:
            fig.update_layout(
                updatemenus=[
                    dict(
                        buttons=[
                            dict(
                                args=[{"visible": [region == reg for region in data['Region']]}],
                                label=reg,
                                method="update"
                            ) for reg in data['Region'].unique()
                        ],
                        direction="down",
                        showactive=True,
                        x=0.1,
                        y=1.15,
                        xanchor="left",
                        yanchor="top",
                        pad={"r": 10, "t": 10},
                    ),
                    dict(
                        buttons=[
                            dict(
                                args=[{"visible": [product == prod for product in data['Product']]}],
                                label=prod,
                                method="update"
                            ) for prod in data['Product'].unique()
                        ],
                        direction="down",
                        showactive=True,
                        x=0.3,
                        y=1.15,
                        xanchor="left",
                        yanchor="top",
                        pad={"r": 10, "t": 10},
                    )
                ]
            )
        fig.show()


# Stage 1: Data Generation
def generate_data():
    try:
        dates = pd.date_range(start="2023-01-01", end="2023-06-30")
        products = ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E']
        regions = ['North', 'South', 'West']

        data = []
        for date in dates:
            for region in regions:
                for product in products:
                    sales = np.random.randint(1000, 5000)
                    data.append([date, region, product, sales])

        df = pd.DataFrame(data, columns=['Date', 'Region', 'Product', 'Sales'])

        # Introduce missing values
        missing_indices = np.random.choice(df.index, 10, replace=False)
        df.loc[missing_indices, 'Sales'] = np.nan

        # Introduce outliers
        outlier_indices = np.random.choice(df.index, 5, replace=False)
        df.loc[outlier_indices, 'Sales'] = np.random.choice([100, 10000], 5)

        df.to_csv('sales_data.csv', index=False)
    except Exception as e:
        logging.error(f"Error generating data: {e}")

# Main script
def main():
    generate_data()

    # Stage 2 and beyond
    sales_data = SalesData('sales_data.csv')
    sales_data.load_data()
    sales_data.clean_data()
    sales_data.save_data('cleaned_sales_data.csv')

    analyzer = DataAnalyzer(sales_data.data)
    total_sales = analyzer.total_sales()
    print("Total Sales:")
    print(total_sales)

    top_product = analyzer.top_product()
    print("Top Product:")
    print(top_product)

    avg_sales = analyzer.average_sales()
    print("Average Monthly Sales:")
    print(avg_sales)

    Visualizer.plot_bar(total_sales, "Total Sales by Region")

    top_product_data = sales_data.data[sales_data.data['Product'] == top_product.index[0]]
    Visualizer.plot_line(top_product_data.groupby('Date')['Sales'].sum(), "Sales Trend for Top Product")

    product_sales = sales_data.data.groupby('Product')['Sales'].sum()
    Visualizer.plot_pie(product_sales, "Percentage Contribution of Each Product")

    # Scatter plot with dropdowns
    Visualizer.plot_interactive(
        sales_data.data,
        chart_type='scatter',
        title="Interactive Scatter Plot: Sales by Date and Region"
    )

    # Bar chart with dropdowns
    Visualizer.plot_interactive(
        sales_data.data,
        chart_type='bar',
        title="Interactive Bar Chart: Sales by Product and Region"
    )

    # Heatmap with dropdowns
    heatmap_data = sales_data.data.pivot_table(index='Region', columns='Product', values='Sales', aggfunc='mean')
    Visualizer.plot_interactive(
        heatmap_data,
        chart_type='heatmap',
        title="Interactive Heatmap: Average Sales per Region and Product"
    )

if __name__ == "__main__":
    main()
