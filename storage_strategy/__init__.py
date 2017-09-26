class GenericStorageStrategy():
    def __init__(self, config):
        self.config = config

    def save_data(self, data, first_time=False):
        raise NotImplementedError("you must implement the save_data method to store data")
