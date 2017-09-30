'''*****************************************************************************************************************
    Raspberry Pi + Raspbian Weather Station
    By Uladzislau Bayouski
    https://www.linkedin.com/in/uladzislau-bayouski-a7474111b/

    Configuration package.
********************************************************************************************************************'''
import configparser


class Config(configparser.ConfigParser):
    """Configuration class for Weather Station"""

    def __init__(self, configfile="config.ini"):
        super(Config, self).__init__()
        self.read(configfile)

    def gettuple(self, section, attr):
        value = self.get(section, attr)
        if (value.startswith('(') and value.endswith(')')):
            string_data = value[1:-1]
            exploded = string_data.split(",")
            return tuple(exploded)
        else:
            raise TypeError("requested value could not be parsed to a tuple")

    def getinttuple(self, section, attr):
        str_tuple = self.gettuple(section, attr)
        int_tuple = [int(x) for x in str_tuple]
        return tuple(int_tuple)

