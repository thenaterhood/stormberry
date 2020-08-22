from stormberry.plugin import IRepositoryPlugin

class Echo(IRepositoryPlugin):

    def store_reading(self, data):
        print(data)
        return True
