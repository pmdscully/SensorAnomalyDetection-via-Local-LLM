# Anomaly Detection on Sensor Data using Docker "Models" Service, local LLM and "AI"-based anomaly detection.

> [!caution]
> Most probably. Don't do this! :-)

## Summary:
The project is an end-to-end pipeline for attempting to detect anomalies in time-series sensor data using a Dockerized environment. It uses Docker Desktop's built-in Model Runner to process data, sent by a container with a python script to send an API request to a local LLM to analyze data and produce a response. Broadly, it's not very reliable (i.e. hallucinations, the bane of LLMs).

> [!note]
> ##### tl;dr.1: We make use of `ai/smollm2:latest` model, and [Docker Model Runner](https://docs.docker.com/ai/model-runner/api-reference/#request-from-the-host-using-tcp) as a service for the local Rest API endpoint, to access the LLM model:
> - Initially, we assume the `data.csv` file will be populated with new sensor information before each `docker compose up` execution.
>     - (*See `helper_data_source.py` for collecting a latest set of data from an InfluxDB table. CSV was tested. Influxdb not tested.)*
> - <img width="730" height="532" alt="image" src="https://github.com/user-attachments/assets/461479c2-e76d-46e1-bec0-8ade3251c1a3" />
> - <img width="629" height="355" alt="image" src="https://github.com/user-attachments/assets/81f93047-8df7-44e5-968c-38501cd8a66a" />


> [!warning]
> ##### tl;dr.2: the results are odd, see `/responses/` directory.
> - "`There are 10 unusual outliers in this temperature data from an office/lab environment with a mean sensor value of 22.4 and standard deviation of 0.9.`"
> - "`There are three unusual outliers in the provided temperature data: 22.7, 22.6, and 22.5 degrees Celsius. The temperature sensor is experiencing issues, resulting in a significant change in the readings.`"
> - "`Unusual temperature readings indicate possible issues in the office or lab environment.`"

---

## How to use:

### Project Files

- **`docker-compose.yml`**: The main orchestration file. It defines the `data-ingestor` service, which runs a transient process to read and process your data.
- **`Dockerfile`**: This file contains the instructions to build the Docker image for the `data-ingestor` service. It installs the necessary Python libraries like `pandas` and `requests`.
- **`process_data.py`**: A Python script that performs the core logic. It reads a `CSV` file, formats the data, sends it to a model's `API` for analysis, and saves the `JSON` response to a file.

### Docker Desktop Setup

Ensure you have a recent version of Docker Desktop (e.g. 4.45.0 - Aug 2025).

Before running this project, you must set up the `Model Runner` in Docker Desktop.

1.  **Enable the Feature**: Navigate to `Settings` > `Beta Features` in Docker Desktop and ensure that `Model Runner` is enabled.
    - Check `Enable Docker Model Runner`
    - Check `Enable host-side TCP support`, to enable HTTP API requests.
    - Set port number (default is ok)
    - Set `CORS Allowed Origins` to `All`. Later, this can be reduced to the single domain of your application (or our transient docker Python process).
    - Apply / Close.
2.  **Download a Model**: In the Docker Desktop dashboard, go to the `Models` section. 
    - Click `Docker Hub` tab.
    - Find and download the compatible language model, `ai/smollm2:latest`, which is used in this project. This is a "small" LLM at 300 MIB model file size.
    - Click `Local` tab. After downloading, the model will be available in this tab to run `>` within Docker Desktop (you can test the prompt-response here.)
3.  **API Endpoint**: 
    - Docker Desktop exposes a single `API` endpoint for all models it runs. 
    - The default port is **12434**. The `docker-compose.yml` is configured to use this endpoint via `http://host.docker.internal:12434/engines/v1/chat/completions`
    - The endpoint accepts a JSON data object structure, in the format described at `https://docs.docker.com/ai/model-runner/api-reference/#request-from-the-host-using-tcp`.

### Build and Run

Follow these steps to build the container and run the anomaly detection process.

1.  **Place Files**: Ensure that all three files (`docker-compose.yml`, `Dockerfile`, and `process_data.py`) are in the same directory, along with a `data.csv` file.
2.  **Open Terminal**: Navigate to the project directory in your terminal.
3.  **Build the Image**: Run the following command to build the Docker image.
    ```bash
    docker compose build
    ```
4.  **Run the Process**: Execute the following command to start the transient container. The container will run the Python script, send the data to the model, and then exit.
    ```bash
    docker compose up
    ```
5.  **Accessing Results**: 
    - The LLM response will be output as a `json` file, e.g. `responses/model_response_YYYYmmdd_HHMMSS.json`
    - Each JSON response filename will be logged into a `results.csv` file.
    - The steps to collect the latest results are as follows:
        1. Read `Results.csv` as Pandas DataFrame.
        2. Sort by `timestamp` column (latest).
        3. Take top column's LLM response filename. e.g. `responses/model_response_YYYYmmdd_HHMMSS.json`
        4. Read response file as JSON.

---

### Issues - Code Changes within Docker Compose:
- If you have changes to the Python code, run the the `docker compose up`, as follows, to ensure the change is executed, and prevent redownloading of Dockerfile packages:
```bash
docker compose up --no-deps --build data-processor
```





