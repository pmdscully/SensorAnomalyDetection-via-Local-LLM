import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.flux_table import FluxTable, FluxRecord

# ----------------------------------------------------------
# --- Get data from local CSV file
# ----------------------------------------------------------

def get_data_from_csv(file_path):
    """
    Reads a CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_json(orient='records')
    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return None


# ----------------------------------------------------------
# --- Get data from InfluxDB
# ----------------------------------------------------------

def get_data_from_influxdb(INFLUXDB_URL,
                           INFLUXDB_TOKEN,
                           INFLUXDB_ORG,
                           INFLUXDB_BUCKET
                           ):
    """
    Queries the latest 100 rows from InfluxDB and returns as a JSON string.
    """
    try:
        with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
            query_api = client.query_api()
            
            # Example Flux query to get the latest 100 rows
            # 'temp' is the measurement and 'sensor-value' is the field
            query = f"""
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -1d)
              |> filter(fn: (r) => r._measurement == "temp")
              |> filter(fn: (r) => r._field == "sensor-value")
              |> last()
            """
            
            tables = query_api.query(query=query)
            
            records = []
            for table in tables:
                for record in table.records:
                    records.append({
                        'timestamp': record.get_time(),
                        'sensor-value': record.get_value()
                    })
            
            df = pd.DataFrame(records)
            return df.to_json(orient='records')
            
    except Exception as e:
        print(f"An error occurred while querying InfluxDB: {e}")
        return None
