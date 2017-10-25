import os
from stormberry.GenericPlugin import GenericPlugin
from yapsy.IPlugin import IPlugin

class Echo(GenericPlugin, IPlugin):

    def set_config(self, config):
        self.config = config

    def save_data(self, data, first_time=False):
        print(data)
