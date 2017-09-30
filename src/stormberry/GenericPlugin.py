class GenericPlugin():

    def save_data(self, data, first_time=False):
        raise NotImplementedError("you must implement the save_data method to store data")
