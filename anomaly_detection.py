import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import os
import sys
import math

plot_filenames = []
additional_data={}
views_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images')) # Absolute path of the images/graph uploaded

def remove_existing_plots():
    for filename in os.listdir('./images'):
        if filename.startswith('plot_') and filename.endswith('.png'):
            os.remove(os.path.join('./images',filename))

# Plot anomaly graph
def plt_anomaly(df,anomalies,str):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time'], df['Value'], color='blue', label='CPU Usage')
    plt.scatter(anomalies['Time'], anomalies['Value'], color='red', label='Anomalies')
    plt.title('Anomalies Detected (Z-Score Method)')
    plt.xlabel('Time')
    plt.ylabel('CPU Usage')
    plt.legend()
    plt.grid(True)
    filename = f'plot_{str}.png'
    plot_filenames.append(filename)
    filepath = os.path.join(views_folder, f'plot_{str}.png')
    plt.savefig(filepath)
    plt.close()

def plt_complete(df,str,col,title):
    plt.figure(figsize=(10, 6))
    # col='Time'
    plt.plot(df[col], df['Value'], color='blue')
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('CPU Usage')
    plt.grid(True)
    filename = f'plot_{str}.png'
    plot_filenames.append(filename)
    filepath = os.path.join(views_folder, f'plot_{str}.png')
    plt.savefig(filepath)
    plt.close()

def plt_anomaly_freq(data,xlabel,title):
    plt.figure(figsize=(10, 6))
    data.plot(kind='bar', color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Anomaly Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f'plot_{xlabel}.png'
    plot_filenames.append(filename)
    filepath = os.path.join(views_folder, f'plot_{xlabel}.png')
    plt.savefig(filepath)
    plt.close() 

def anomaly_detect(csv_file):
    df = pd.read_csv(csv_file)
    df['Time'] = pd.to_datetime(df['Time'])
    df["Separate_Time"]=df['Time'].dt.time
    df['Date'] = df['Time'].dt.date
    plt_complete(df,"complete",'Time',"CPU Usage Over Time")

    df['Z-Score'] = (np.log(df['Value']) - np.log(df['Value']).mean()) / np.log(df['Value']).std() # Calculating the Z score by making the distribution normal using log transformation

    # Set threshold for anomaly detection
    threshold = 2
    additional_data["Z Score Threshold"]=2
    anomalies = df[df['Z-Score'].abs() > threshold]

    plt_anomaly(df,anomalies,"anomalies_complete")

    # CPU Thresholds
    threshold_cpu_upper = np.log(df['Value']).mean() + (threshold * np.log(df['Value']).std())
    threshold_cpu_lower = np.log(df['Value']).mean() - (threshold * np.log(df['Value']).std())

    threshold_cpu_upper = math.exp(threshold_cpu_upper)
    threshold_cpu_lower = math.exp(threshold_cpu_lower)
    additional_data["Upper Threshold CPU Usage"]= threshold_cpu_upper
    additional_data["Lower Threshold CPU Usage"]= threshold_cpu_lower

    anomalies['Hour'] = anomalies['Time'].dt.hour
    hourly_data = anomalies.groupby('Hour').size()

    plt_anomaly_freq(hourly_data,"Hourly",'Anomaly Frequency by Hour')

    day_data = anomalies.groupby('Date').size()
    plt_anomaly_freq(day_data,"Daywise",'Anomaly Frequency by Day')



if __name__ == '__main__':
    remove_existing_plots()
    csv_file = sys.argv[1]

    anomaly_detect(csv_file)
    output = json.dumps({'plots': plot_filenames,'data': additional_data})

    print(output)  # Print the JSON output