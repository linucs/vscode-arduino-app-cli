from _typeshed import Incomplete
from arduino.app_utils import brick as brick
from dataclasses import dataclass

city_api_url: str
forecast_api_url: str

@dataclass(frozen=True)
class WeatherData:
    '''Weather forecast data with standardized codes and categories.

    Attributes:
        code (int): WMO weather code representing specific weather conditions.
        description (str): Human-readable weather description (e.g., "Partly cloudy", "Heavy rain").
        category (str): Simplified weather category: "sunny", "cloudy", "rainy", "snowy", or "foggy".
    '''
    code: int
    description: str
    category: str

weather_data: Incomplete

class WeatherForecast:
    """Weather forecast service using the open-meteo.com API.

    Provides weather forecasts by city name or geographic coordinates with no API key required.
    Returns structured weather data with WMO codes, descriptions, and simplified categories.
    """
    def get_forecast_by_city(self, city: str, timezone: str = 'GMT', forecast_days: int = 1) -> WeatherData:
        '''Get weather forecast for a specified city.

        Args:
            city (str): City name (e.g., "London", "New York").
            timezone (str): Timezone identifier. Defaults to "GMT".
            forecast_days (int): Number of days to forecast. Defaults to 1.

        Returns:
            WeatherData: Weather forecast with code, description, and category.

        Raises:
            RuntimeError: If city lookup or weather data retrieval fails.
        '''
    def get_forecast_by_coords(self, latitude: str, longitude: str, timezone: str = 'GMT', forecast_days: int = 1) -> WeatherData:
        '''Get weather forecast for specific coordinates.

        Args:
            latitude (str): Latitude coordinate (e.g., "45.0703").
            longitude (str): Longitude coordinate (e.g., "7.6869").
            timezone (str): Timezone identifier. Defaults to "GMT".
            forecast_days (int): Number of days to forecast. Defaults to 1.

        Returns:
            WeatherData: Weather forecast with code, description, and category.

        Raises:
            RuntimeError: If weather data retrieval fails.
        '''
    def process(self, item):
        '''Process dictionary input to get weather forecast.

        This method checks if the item is a dictionary with latitude and longitude or city name.
        If it is a dictionary with latitude and longitude, it retrieves the weather forecast by coordinates.
        If it is a dictionary with city name, it retrieves the weather forecast by city.

        Args:
            item (dict): Dictionary with either "city" key or "latitude"/"longitude" keys.

        Returns:
            WeatherData | dict: WeatherData object if valid input provided, empty dict if input format is invalid.

        Raises:
            CityLookupError: If the city is not found.
            WeatherForecastLookupError: If the weather forecast cannot be retrieved.
        '''

class CityLookupError(Exception):
    """Exception raised when the city lookup (geocoding) fails."""
class WeatherForecastLookupError(Exception):
    """Exception raised when the weather forecast lookup fails."""
