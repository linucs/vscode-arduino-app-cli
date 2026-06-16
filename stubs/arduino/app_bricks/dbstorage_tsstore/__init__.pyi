from _typeshed import Incomplete
from arduino.app_internal.core import get_brick_compose_file as get_brick_compose_file, parse_docker_compose_variable as parse_docker_compose_variable
from arduino.app_utils import Logger as Logger, brick as brick
from influxdb_client import InfluxDBClient
from typing import Any

logger: Incomplete
base_influx_host: str
base_influx_port: int

class TimeSeriesStoreError(Exception):
    """Custom exception raised for TimeSeriesStore database operation errors."""

class _InfluxDBHandler:
    """Base class for handling InfluxDB connections and operations.

    This class initializes the InfluxDB client and provides methods for writing and querying data.
    It automatically loads configuration from Docker Compose infrastructure and manages
    database authentication, bucket settings, and connection parameters.

    Note:
        It is intended to be subclassed for specific database operations. Use TimeSeriesStore for time series operations.
    """
    name: str
    host: Incomplete
    port: Incomplete
    url: Incomplete
    token: Incomplete
    org: Incomplete
    bucket: Incomplete
    client: InfluxDBClient
    retention_days: Incomplete
    def __init__(self, host: str = ..., port: int = ..., retention_days: int = 7) -> None:
        '''Initialize the InfluxDB client with the provided host and port.

        Args:
            host (str, optional): The hostname of the InfluxDB server. Defaults to "dbstorage-influx".
            port (int, optional): The port number of the InfluxDB server. Defaults to 8086.
            retention_days (int, optional): Number of days to retain data in the InfluxDB bucket. Defaults to 7.
        '''
    write_api: Incomplete
    query_api: Incomplete
    def start(self) -> None:
        """Establish a connection to the InfluxDB server.

        This method creates the InfluxDB client connection, initializes write and query APIs,
        and configures the data retention policy for the bucket. The connection is established
        with the parameters specified during initialization.

        Raises:
            TimeSeriesStoreError: If there is an error connecting to the InfluxDB server.
        """
    def stop(self) -> None:
        """Close the InfluxDB database connection.

        Properly closes the client connection and releases associated resources.
        Should be called when finished with the time series store to ensure
        proper cleanup.
        """
    def load_default_infra(self):
        """Load the default InfluxDB compose file for the brick.

        This method looks for a YAML file named 'module_compose.yaml' in the current module's directory.
        If the file is found, it loads the content and returns it as a dictionary.
        If the file is not found, it logs an error message.

        Returns:
            dict: The content of the compose file as a dictionary.
        """
    def get_client(self) -> InfluxDBClient:
        """Returns the InfluxDB client instance."""

class TimeSeriesStore(_InfluxDBHandler):
    """Time series database handler for storing and retrieving data using InfluxDB.

    This class extends the base InfluxDB handler and provides methods for writing samples to the database.
    It allows writing and reading individual measurements with their values and timestamps.
    """
    def __init__(self, host: str = ..., port: int = ..., retention_days: int = 7) -> None:
        '''Initialize the InfluxDB persistence handler.

        Args:
            host (str, optional): The hostname of the InfluxDB server.
                Defaults to "dbstorage-influx".
            port (int, optional): The port number of the InfluxDB server.
                Defaults to 8086.
            retention_days (int, optional): The number of days to retain data in the
                InfluxDB bucket. Defaults to 7.
        '''
    def write_sample(self, measure: str, value: Any, ts: int = 0, measurement_name: str = 'arduino'):
        '''Write a time series sample to the InfluxDB database.

        Stores a single data point with the specified measurement field, value, and timestamp.
        If no timestamp is provided, the current time is used automatically.

        Args:
            measure (str): The name of the measurement field (e.g., "temperature", "humidity").
                This acts as the column name for the data point.
            value (Any): The numeric or string value to store. Supports int, float, str, and bool types.
            ts (int, optional): The timestamp in milliseconds since epoch.
                Defaults to 0 (current time).
            measurement_name (str, optional): The measurement container name that groups
                related fields together. Defaults to "arduino".

        Raises:
            TimeSeriesStoreError: If there is an error writing the sample to the InfluxDB database,
                such as connection failures or invalid data types.
        '''
    def read_last_sample(self, measure: str, measurement_name: str = 'arduino', start_from: str = '-1d') -> tuple | None:
        '''Read the last sample of a specific measurement from the InfluxDB database.

        Retrieves the latest data point for the specified measurement field within
        the given time range.

        Args:
            measure (str): The name of the measurement field to query (e.g., "temperature").
            measurement_name (str, optional): The measurement container name to search within.
                Defaults to "arduino".
            start_from (str, optional): The time range to search within. Supports relative
                periods like "-1d" (1 day), "-2h" (2 hours), "-30m" (30 minutes) or
                RFC3339 timestamps like "2024-01-01T00:00:00Z". Defaults to "-1d".

        Returns:
            tuple | None: A tuple containing (field_name, timestamp_iso, value) where:
                - field_name (str): The measurement field name
                - timestamp_iso (str): ISO format timestamp string
                - value (Any): The stored value
                Returns None if no data is found in the specified time range.

        Raises:
            TimeSeriesStoreError: If the start_from value is invalid or if there is an error querying the InfluxDB database.
        '''
    def read_samples(self, measure: str, measurement_name: str = 'arduino', start_from: str = '-1d', end_to: str = None, aggr_window: str = None, aggr_func: str = None, limit: int = 1000, order: str = 'asc') -> list:
        '''Read all samples of a specific measurement from the InfluxDB database.

        Retrieves multiple data points for the specified measurement field with support
        for time range filtering, data aggregation, and result ordering.

        Args:
            measure (str): The name of the measurement field to query (e.g., "temperature").
            measurement_name (str, optional): The measurement container name to search within.
                Defaults to "arduino".
            start_from (str, optional): The start time for the query range. Supports relative
                periods ("-7d", "-1h") or RFC3339 timestamps. Defaults to "-1d".
            end_to (str, optional): The end time for the query range. Supports same formats
                as start_from or "now()". Defaults to None (current time).
            aggr_window (str, optional): Time window for data aggregation (e.g., "1h" for hourly,
                "30m" for 30-minute intervals). Must be used with aggr_func. Defaults to None.
            aggr_func (str, optional): Aggregation function to apply within each window.
                Supported values: "mean", "max", "min", "sum". Must be used with aggr_window.
                Defaults to None.
            limit (int, optional): Maximum number of samples to return. Must be positive.
                Defaults to 1000.
            order (str, optional): Sort order for results by timestamp. Must be "asc"
                (ascending, oldest first) or "desc" (descending, newest first). Defaults to "asc".

        Returns:
            list: List of tuples, each containing (field_name, timestamp_iso, value) where:
                - field_name (str): The measurement field name
                - timestamp_iso (str): ISO format timestamp string
                - value (Any): The stored or aggregated value
                Empty list if no data found in the specified range.

        Raises:
            TimeSeriesStoreError: If any parameter is invalid, such as:
                - Invalid time format in start_from or end_to
                - Invalid order value (not "asc" or "desc")
                - Invalid limit value (not positive integer)
                - Invalid aggregation function
                - Mismatched aggr_window and aggr_func (one specified without the other)
                - Database query errors
        '''
