## Anomaly Detection Pipeline

This project demonstrates an end-to-end pipeline for detecting anomalies in time-series sensor data using a Dockerized environment. It uses Docker Desktop's built-in Model Runner to process data and an LLM to analyze the results.

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
    - The default port is **12434**. The `docker-compose.yml` is configured to use this endpoint via `http://model-runner.docker.internal:12434` or `http://localhost:12434/engines/v1/chat/completions`
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

If you have changes to the Python code, run the the `docker compose up`, as follows, to ensure the change is executed, and prevent redownloading of Dockerfile packages:
```sh
docker compose up --no-deps --build data-processor
```
