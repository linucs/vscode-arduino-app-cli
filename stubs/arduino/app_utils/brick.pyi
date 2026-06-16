from _typeshed import Incomplete

class BrickDecorator:
    """A class that acts as a namespace for the brick decorators to avoid name clashes with user code.
    - @brick is the main class decorator used to transform a class into an Arduino brick.
    - @brick.loop and @brick.execute are the method decorators used to hook them to the AppController.
    """
    def __call__(self, user_class=None):
        """Handles decorating the class.
        Can be used as @brick or @brick().
        """
    def execute(self, _func=None):
        """Method decorator that marks a method as a one-shot, blocking tasks.
        The AppController will run this method only once, in a dedicated thread.
        Can be used as @brick.execute or @brick.execute().
        """
    def loop(self, _func=None):
        """Method decorator that marks a method as a non-blocking, iterative tasks.
        The AppController will run this method repeatedly, in a dedicated thread.
        Can be used as @brick.loop or @brick.loop().
        """

brick: BrickDecorator
