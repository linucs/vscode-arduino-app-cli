from .logger import Logger as Logger
from _typeshed import Incomplete

logger: Incomplete

class AppController:
    """AppController orchestrates the entire application lifecycle by managing brick startup, shutdown, and their
    loops execution in a controlled, structured way.

    It discovers methods named 'loop'/'execute' or decorated with @loop/@execute and runs each in a separate thread.
    Also methods named 'start' and 'stop' are called automatically depending on the App's lifecycle.

    Bricks that are instantiated before App.run() is called will be started/stopped automatically.
    Bricks that are started manually via App.start_brick() must have their lifecycle managed manually by the user.

    When App.run() exits, all bricks, including those started manually, will be stopped to ensure a clean shutdown.
    """
    def __init__(self) -> None: ...
    def register(self, brick) -> None:
        """Registers a brick for being managed automatically by the AppController.

        If the brick is not running, it will be auto-started when App.run() will be called.
        If the brick is already running, this method does nothing.
        """
    def unregister(self, brick) -> None:
        """Unregisters a brick from being managed automatically by the AppController.

        If the brick is not running, it won't be auto-started anymore when App.run() will be called.
        If the brick is already running, this method does nothing.
        """
    def start_bricks(self) -> None:
        """Starts the application and all registered bricks.

        Use this method if you don't want to block the main thread and handle it as you wish.

        The bricks should be manually managed by the user by calling App.stop_bricks().
        """
    def start_brick(self, brick) -> None:
        """Immediately starts a single brick and all its runnable methods.

        This brick should be manually managed by the user by calling App.stop_brick().
        """
    def stop_bricks(self) -> None:
        """Stops the application and all running bricks."""
    def stop_brick(self, brick) -> None:
        """Immediately stops a single running brick."""
    def run(self, user_loop: callable = None):
        """Starts all registered bricks and keeps the main thread alive, waiting for a shutdown signal (Ctrl+C).

        If a user_loop callable is provided, it will be executed instead of the default infinite loop.

        Args:
            user_loop (callable, optional): A user-defined function to run instead of the default infinite loop.
        """
    def loop(self, user_loop: callable = None):
        """This method keeps the application running, blocking until a KeyboardInterrupt (Ctrl+C) occurs.

        If a user_loop callable is provided, it will be executed inside an infinite loop and
        called repeatedly every iteration.

        Args:
            user_loop (callable, optional): A user-defined function to run inside an infinite loop.
        """

App: AppController
