from abc import ABCMeta, abstractmethod, abstractproperty

class CarouselContainer(object):
    """
    Base class for carousel like classes.

    These classes contain list of items, and iterate through them functionality.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        # Index of current carousel item
        self.current_index = 0

    @abstractproperty
    def carousel_items(self):
        """Carousel items to iterate through."""
        pass

    @property
    def next_item(self):
        """
        Gets next item, and sets its index as current_index.

        If item is the last one returns the first item.
        """
        if self.current_index < len(self.carousel_items) - 1:
            self.current_index += 1
        else:
            self.current_index = 0

        return self.current_item

    @property
    def previous_item(self):
        """
        Gets previous item, and sets its index as current_index.

        If item is the first one returns the last item.
        """
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.carousel_items) - 1

        return self.current_item

    @property
    def current_item(self):
        """Returns current item."""
        return self.carousel_items[self.current_index]


