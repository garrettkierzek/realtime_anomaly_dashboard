This project repository is created in partial fulfillment of the requirements for the Big Data Analytics course offered by the Master of Science in Business Analytics program at the Carlson School of Management, University of Minnesota.

# Real-Time Anomaly Detection in Industrial IoT using Kafka, Isolation Forest, and GPT

This project simulates a real-time industrial manufacturing environment, using modern big data and AI technologies to detect and explain anomalies in sensor data streams.

## Executive Summary

This project simulates a real-time industrial IoT quality monitoring system using modern big data and AI technologies. It mimics a high-throughput manufacturing environment where sensor data—such as temperature, vibration, pressure, and speed—is continuously streamed using Apache Kafka.

A Python-based Kafka consumer ingests the data, applies an unsupervised Isolation Forest model to detect potential anomalies, and calls the OpenAI GPT model to generate natural language explanations for flagged events. The results are logged to both a SQLite database and a CSV file to support real-time visualization. In reality, such practices could be expanded to a much larger feature set, in which, AI explainability would be able to quickly identify the source(s) of the anomaly and make recommendations about where to start in terms of finding a solution.

Instead of relying on static business intelligence tools, this project leverages Streamlit to build a live, interactive web dashboard that highlights key trends and automatically updates as new sensor readings and anomalies flow in. The dashboard displays sensor values, anomaly scores, and AI-generated recommendations to support proactive quality control.

The goal is to demonstrate how modern data streaming, machine learning, and generative AI can work together to improve operational transparency, reduce downtime, and enhance decision-making in smart manufacturing environments, as well as highlight a traditional big data pipeline that can manage high volume and velocity.

## Project Components

| Module               | Description                                                     |
|----------------------|-----------------------------------------------------------------|                      
| `producer.py`        | Streams synthetic sensor data into Kafka topic                  |
| `consumer.py`        | Detects anomalies using Isolation Forest + GPT explanations     |
| `docker-compose.yml` | Sets up Kafka and Zookeeper via Docker                          |
| `dashboard_data.db`  | Live data store for Streamlit visualization                     |
| `streamlit_app.py`   | Live web dashboard for monitoring system health and anomalies   |

## Steps to Recreate

### Initialize Docker Container
1. Download Docker desktop (https://www.docker.com/products/docker-desktop/), follow installation instructions, run as administrator
2. Create a folder called Kafka_env, put `producer.py`, `consumer.py`, `docker-compose.yml` into the folder
3. Open powershell/command prompt as administrator, set working directory to Kafka_env folder, i.e. 'cd D:\BigDataAnalytics\TrendsMarketplace\kafka_env'  
4. Also in powershell/command prompt, run 'docker-compose up -d' to initialize the kafka/zookeeper container
5. Note, in docker desktop your kafka_env container will not be visible 

### Create Synthetic Dataset
1. In your terminal run 'pip install -r requirements.txt' to initialize all packages in your virtual environment
2. To control the size, strength and frequency of anomalies, and more we created our own dataset for the sake of demonstrating the pipline
3. To create this dataset, run the provided code `synthetic_data.ipynb`
4. From this point you can utilize the saved csv, in the producer

### Running Producer and Consumers
1. In your IDE open the `producer.py` file and run, wait for data to start outputting
2. Prior to loading and running `consumer.py`, in order to utilize GPT explainability, one must create an OpenAI account (https://openai.com/api) and navigate to settings to obtain an api key.
3. open the `consumer.py` file and insert your api key from OpenAI, run and wait for consumer to start ingesting

### Launching Dashboard
1. Using the `machine_dashboard.py` file, run streamlit run machine_dashboard.py in your terminal to open the dashboard in a browser
2. Interact with the dashboard by selecting the machine ID, you would like to see anomaly reasoning for
3. Zoom and pan in and out of line charts with ctrl + scroll or ctrl + click

### Additional Resources
1. [link1](https://docs.streamlit.io/)
2. [link2]https://kafka-python.readthedocs.io/en/master/
3. [link3]https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html


### Project Materials
- [Project Flyer (PDF)](./project_flyer.pdf)


