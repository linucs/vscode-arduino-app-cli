from .logger import Logger as Logger
from _typeshed import Incomplete

logger: Incomplete
ROUTE_ALREADY_EXISTS_ERR: int
BUFFER_LIMIT_EXCEEDED_ERR: int
MALFORMED_CALL_ERR: int
FUNCTION_NOT_FOUND_ERR: int
GENERIC_ERR: int

class Bridge:
    @staticmethod
    def notify(method_name: str, *params):
        '''Sends a notification to the microcontroller without waiting for a response.

        Args:
            method_name (str): The name of the method to notify on the microcontroller.
            *params: The parameters to pass to the method.

        Examples:
            Bridge.notify("set_led", "green", True)
            Bridge.notify("log_message", "Hello, microcontroller!")
        '''
    @staticmethod
    def call(method_name: str, *params, timeout: int = 10):
        '''Calls a method on the microcontroller and waits for a response.
        Raises an exception if the call fails or times out.

        Args:
            method_name (str): The name of the method to call on the microcontroller.
            *params: The parameters to pass to the method.
            timeout (int, optional): The maximum time to wait for a response in seconds. Defaults to 10s.

        Raises:
            ValueError: If the method does not exist.
            TimeoutError: If the call takes more time than the specified timeout.
            RuntimeError: If the call fails unexpectedly.

        Examples:
            temperature = Bridge.call("get_temperature", "sensor1")
            print(f"Temperature: {temperature}")
        '''
    @staticmethod
    def provide(method_name: str, handler: callable):
        '''Makes a method available to the microcontroller, so it can call it remotely.
        The handler should be a callable that can take arguments.

        Args:
            method_name (str): The name under which the function should be provided to the microcontroller.
            handler (callable): The function to call when the microcontroller requires it.

        Raises:
            ValueError: If handler is not callable.
            RuntimeError: If the request fails unexpectedly.

        Examples:
            def get_country(lon: str, lat: str) -> str:
                ... lookup country by lon and lat ...
                return country_name

            Bridge.provide("get_country", get_country)
        '''
    @staticmethod
    def unprovide(method_name: str):
        '''Makes a method no more available to the microcontroller.

        Args:
            method_name (str): The name under which the function is already provided to the microcontroller.

        Raises:
            RuntimeError: If the request fails unexpectedly.

        Examples:
            Bridge.unprovide("get_country")
        '''

def notify(method_name: str = None, address: str = 'unix:///var/run/arduino-router.sock'):
    '''Decorator that transforms a function into a notification for the microcontroller.

    When the decorated function is called, an RPC \'notify\' (fire-and-forget) is sent
    to the microcontroller. The notify\'s arguments are taken from the decorated function\'s arguments.
    The RPC method name defaults to the decorated function\'s name if not specified.

    Args:
        method_name (str, optional): The name of the RPC method to call. Defaults to the decorated function\'s name.
        address (str, optional): The address of the microcontroller router to connect to. Can be a TCP socket or a Unix socket. Defaults to "unix:///var/run/arduino-router.sock".

    Raises:
        TypeError: If the decorated function is called with unexpected keyword arguments.

    Examples:
        @notify()
        def set_led(color: str, status: bool): ... # Body is not needed

        @notify("leds.green.set_status", timeout=3)
        def set_green_led(status: bool): ...

        set_led("green", True) # Sends "set_led" RPC notification
        set_green_led(True) # Sends "leds.green.set_status" RPC notification
    '''
def call(method_name: str = None, timeout: int | None = 10, address: str = 'unix:///var/run/arduino-router.sock'):
    '''Decorator that transforms a function into an RPC notification.

    When the decorated function is called, an RPC \'call\' (request and response) is sent
    to the microcontroller. The call\'s arguments are taken from the decorated function\'s arguments.
    The RPC method name defaults to the decorated function\'s name if not specified.
    A default timeout for the RPC call can be set via the decorator but it can be overridden.
    by passing a \'timeout\' keyword argument when calling the decorated function.

    Args:
        method_name (str, optional): The name of the RPC method to call. Defaults to the decorated function\'s name.
        timeout (int, optional): The maximum time to wait for a response in seconds. If None, waits indefinitely. Defaults to 10s.
        address (str, optional): The address of the microcontroller router to connect to. Can be a TCP socket or a Unix socket. Defaults to "unix:///var/run/arduino-router.sock".

    Raises:
        TypeError: If the decorated function is called with unexpected keyword arguments.
        ValueError: If the method does not exist.
        TimeoutError: If the call takes more time than the specified timeout.
        RuntimeError: If the call fails unexpectedly.

    Examples:
        @call()
        def get_led(color: str) -> bool: ... # Body is not needed

        @call("leds.green.status", timeout=3)
        def get_green_led() -> bool: ...

        state = get_led("green")
        state = get_green_led()
    '''
def provide(method_name=None, address: str = 'unix:///var/run/arduino-router.sock'):
    '''Decorator that makes a method available to the microcontroller, so it can call it remotely.

    The decorated function is automatically registered using its own name as method name,
    unless `method_name` is provided.

    Args:
        method_name (str, optional): The name under which the function should be registered.
        address (str, optional): The address of the microcontroller router to connect to. Can be a TCP socket or a Unix socket. Defaults to "unix:///var/run/arduino-router.sock".

    Raises:
        ValueError: If handler is not callable.
        RuntimeError: If the request fails unexpectedly.

    Examples:
        @provide()
        def get_country(lon: str, lat: str) -> str:
            ... lookup country by lon and lat ...
            return country_name

        @provide("custom.rpc.name")
        def another_handler(param):
            ... logic ...
    '''

class SingletonMeta(type):
    def __call__(cls, *args, **kwargs): ...

class ClientServer(metaclass=SingletonMeta):
    next_msgid: int
    next_msgid_lock: Incomplete
    callbacks: Incomplete
    callbacks_lock: Incomplete
    handlers: Incomplete
    handlers_lock: Incomplete
    socket_type: str
    def __init__(self, address: str = 'unix:///var/run/arduino-router.sock') -> None: ...
    def notify(self, method_name: str, *params):
        """Sends a notification to the server without waiting for a response."""
    def call(self, method_name: str, *params, timeout: int = 10):
        """Calls a method on the server and waits for a response."""
    def provide(self, method_name: str, handler):
        """Makes a method available to the microcontroller, so it can call it remotely.
        The handler should be a callable that can take arguments.
        """
    def unprovide(self, method_name: str):
        """Makes a method no more available to the microcontroller."""
