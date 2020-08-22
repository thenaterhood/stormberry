from yapsy.IPlugin import IPlugin

class PluginDataManager():
    '''
    Just a central data manager for plugins that need to share a single
    entity. This primarily powers the Pi Sense Hat so the entity can be
    used by both a sensor plugin and a display plugin
    '''
    def __init__(self):
        self.__data = dict()

    def get_entity(self, key):
        if key in self.__data:
            return self.__data[key]

        return None

    def store_entity(self, key, value):
        if key in self.__data:
            raise Exception("Entity already exists")

        self.__data[key] = value

    def del_entity(self, key):
        if key in self.__data:
            del self.__data[key]


class IRepositoryPlugin(IPlugin):

    def activate(self, config, data_manager):
        '''
        Activate the plugin. This should set up whatever callbacks
        and connections this plugin intends to have in addition to
        the two defined by stormberry's plugin API.
        '''
        self.config = config
        self.data_manager = data_manager
        return True

    def deactivate(self):
        '''
        Called on shutdown or to reinitialize. Expected to close
        all connections and files as needed for a clean shutdown.
        '''
        pass

    def store_reading(self, reading):
        '''
        Store a weather reading

        Returns:
            True (success) or False (fail)
        '''
        return True

    def get_health(self):
        '''
        Health check method. Returns True (healthy) or False (unhealth)
        '''
        return True


class ISensorPlugin(IPlugin):

    def activate(self, config, data_manager):
        '''
        Activate the plugin. This should set up whatever callbacks
        and connections this plugin intends to have in addition to
        the two defined by stormberry's plugin API.
        '''
        self.config = config
        self.data_manager = data_manager
        return True

    def deactivate(self):
        '''
        Called on shutdown or to reinitialize. Expected to close
        all connections and files as needed for a clean shutdown.
        '''
        pass

    def get_reading(self):
        '''
        Assemble and return a weather reading

        Returns:
            WeatherReading or None
        '''
        return None

    def get_health(self):
        '''
        Health check method. Returns True (healthy) or False (unhealth)
        '''
        return True


class IDisplayPlugin(IPlugin):
    '''
    A very basic display plugin for handling complex display needs. This is largely
    identical to the repository plugin but does not allow reading weather data.
    '''

    def activate(self, config, data_manager):
        self.config = config
        self.data_manager = data_manager
        return True

    def deactivate(self):
        pass

    def update(self, weather_reading):
        return True

