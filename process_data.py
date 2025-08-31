import pandas as pd
import requests
import json
import os
import datetime

from helper_data_sources import get_data_from_csv, get_data_from_influxdb

# Configuration from environment variables
MODEL_API_URL = os.getenv("MODEL_API_URL")
PROMPT = os.getenv("PROMPT")
CSV_PATH = "/app/data.csv"
RESULTS_FILE_PATH = "/app/results.csv"
RESPONSES_JSON_PATH = '/app/responses'

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

def update_results_file(api_url, output_filename):
    """
    Appends the run details to a results CSV file.
    """
    try:
        if not os.path.exists(RESULTS_FILE_PATH):
            df = pd.DataFrame(columns=['timestamp', 'model_api_url', 'output_filename'])
            df.to_csv(RESULTS_FILE_PATH, index=False)
            print("Created a new results file.")

        timestamp = datetime.datetime.now().isoformat()
        new_row = pd.DataFrame([{
            'timestamp': timestamp,
            'model_api_url': api_url,
            'output_filename': output_filename
        }])
        
        new_row.to_csv(RESULTS_FILE_PATH, mode='a', header=False, index=False)
        print(f"Updated results file with new entry.")

    except Exception as e:
        print(f"Error updating results file: {e}")

def main():
    """
    Main function to read data and send to the model API.
    """
    print("Starting transient data processing...")

    # Step 1: Read the data
    # json_data = get_data_from_influxdb(INFLUXDB_URL,
    #                                 INFLUXDB_TOKEN,
    #                                 INFLUXDB_ORG,
    #                                 INFLUXDB_BUCKET
    #                                 )
    json_data = get_data_from_csv(CSV_PATH)
    if json_data is None:
        return

    # Step 2: Construct the payload for the model API
    payload = {
        "model": "ai/smollm2",  # Adjust model name as needed
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful data analyst that can detect anomalies."
            },
            {
                "role": "user",
                "content": f"{PROMPT}\n\nHere is the data in JSON format: {json_data}"
            }
        ]
    }

    # Step 3: Send the request to the model API
    try:
        print("Sending data to the model for analysis...")
        response = requests.post(MODEL_API_URL, json=payload, timeout=600)
        response.raise_for_status()
        
        # Print the model's response
        model_output = response.json()
        print("\n--- Model Response ---")
        print(json.dumps(model_output, indent=2))
        print("\n--------------------")

        print("\n--- Write Model Response to JSON ---")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_filename = f"{RESPONSES_JSON_PATH}/model_response_{timestamp}.json"
        os.makedirs(RESPONSES_JSON_PATH, exist_ok=True)
        with open(output_filename, 'w') as f:
            json.dump(model_output, f, indent=2)
        
        print("\n--------------------")
        # Step 4: Update the results file
        update_results_file(MODEL_API_URL, output_filename)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with the model API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Process complete. Exiting.")

if __name__ == "__main__":
    main()