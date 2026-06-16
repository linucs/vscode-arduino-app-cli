from _typeshed import Incomplete

application_config_file_name: str
config_file_name: str
compose_config_file_name: str

def get_app_config() -> dict | None:
    """Gets app.yaml application configuration."""
def get_brick_config(cls) -> dict | None:
    """Gets resolved brick_config.yaml file."""
def get_brick_config_file(cls) -> str | None:
    """Gets the full path of the brick_config.yaml file."""
def get_brick_compose_file(cls) -> str | None:
    """Gets the full path of the brick_compose.yaml file, if present."""
def load_brick_compose_file(cls) -> dict | None:
    """Loads the brick_compose.yaml file and returns its content."""
def get_brick_linked_resource_file(cls, resource_file_name) -> str | None:
    """Gets the full path to a config file in the directory containing a class."""
def get_brick_configured_model(brick_id: str) -> str | None:
    """Helper method to extract the model name from the app configuration for this brick.
    This allows dynamic configuration of the model via the app's config file, overriding defaults.

    Model is part of the brick configuration in the app config file, under the specific brick's entry. The structure is:

    bricks:
    - arduino:llm:
        model: genie:qwen3-4b

    Args:
        brick_id (str): The identifier of the brick for which to retrieve the model configuration.
    Returns:
        Optional[str]: The model name if found in the app configuration, otherwise None.
    Raises:
        ValueError: If `brick_id` is not provided (empty string).
    """
def parse_docker_compose_variable(variable_string) -> list[tuple[str, str]] | str:
    '''Parses a Docker Compose-style environment variable string, including nested variables.

    Args:
        variable_string: The string to parse (e.g., "${DATABASE_HOST:-db}",
            "${BIND_ADDRESS:-127.0.0.1}:8086:8086"), "${DATABASE_PASSWORD}".

    Returns:
        A list of tuple containing the variable name and the default value (if present), or the original
        string if parsing fails.
    '''

class ModuleVariable:
    name: Incomplete
    default_value: Incomplete
    description: Incomplete
    def __init__(self, name: str, description: str, default_value: str = None) -> None:
        """Represents a variable in a Docker Compose file."""
    def to_dict(self) -> dict:
        """Converts the ModuleVarable object to a dictionary."""

class EnvVariable:
    name: Incomplete
    default_value: Incomplete
    description: Incomplete
    hidden: Incomplete
    secret: Incomplete
    def __init__(self, name: str, description: str, default_value: str = None, hidden: bool = False, secret: bool = False) -> None:
        """Represents a variable in brick_config file."""
    def to_dict(self) -> dict:
        """Converts the EnvVariable object to a dictionary."""

def load_module_supported_variables(file_path: str) -> list[ModuleVariable] | None:
    """Loads a Docker Compose file and returns all supported variables with its default values and description.

    Returns:
        A list of ModuleVarable objects representing the variables found in the Docker Compose file.
    """
def resolve_address(host: str) -> str:
    """Resolve address substituting it in case of local/remote development."""
