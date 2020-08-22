from yapsy.PluginManager import PluginManager
from stormberry.plugin import ISensorPlugin, IRepositoryPlugin, IDisplayPlugin

class PluginTypeName:
    SENSOR = 'Sensor'
    DISPLAY = 'Display'
    REPOSITORY = 'Repository'

def get_plugin_manager(config):
    plugin_manager = PluginManager()

    plugin_manager.setPluginPlaces(
            [config.get("GENERAL", "PLUGIN_DIRECTORY")]
            )

    plugin_manager.setCategoriesFilter({
        PluginTypeName.SENSOR: ISensorPlugin,
        PluginTypeName.REPOSITORY: IRepositoryPlugin,
        PluginTypeName.DISPLAY: IDisplayPlugin
    })

    plugin_manager.collectPlugins()

    return plugin_manager
