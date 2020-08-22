from stormberry.plugin import PluginDataManager
from stormberry.plugin.manager import PluginTypeName, get_plugin_manager
from stormberry.config import Config

def get_repository():
    repository = None

    config = Config()
    plugin_manager = get_plugin_manager(config)
    plugin_data_manager = PluginDataManager()

    try:
        preferred_repo = config.get("GENERAL", "SERVER_DATA_SOURCE")
        repository = plugin_manager.getPluginByName(preferred_repo, PluginTypeName.REPOSITORY).plugin_object
        repository.prepare(config, plugin_data_manager)
    except:
        for p in plugin_manager.getPluginsOfCategory(PluginTypeName.REPOSITORY):
            p.plugin_object.prepare(config, plugin_data_manager)
            if p.plugin_object.get_latest() is not None:
                repository = p.plugin_object
                break

    if repository is None:
        raise Exception("No acceptable data source found")

    return repository

