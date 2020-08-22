import stormberry.plugin

class Echo(stormberry.plugin.IRepositoryPlugin):

    def store_reading(self, data):
        print(data)
        return True
