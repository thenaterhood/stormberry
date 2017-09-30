class GenericPlugin():

    def set_config(self, config):
        '''
        Passes the configuration to the plugin class so configuration
        information is available.
        '''
        self.config = config

    def save_data(self, data, first_time=False):
        '''
        Saves weather data
        '''
        raise NotImplementedError("you must implement the save_data method to store data")
