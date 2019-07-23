import importlib
import os
import sys

# https://stackoverflow.com/questions/21367320/searching-for-equivalent-of-filenotfounderror-in-python-2/21368622#21368622
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class Plugin:
    """ Plugin System """

    def __init__(self, PluginFolder="plugins", MainModule="__init__.py", provider='ansible'):
        self.PluginFolder = PluginFolder
        self.Provider = provider
        self.MainModule = MainModule

    def getPlugins(self, PluginFolder):
        plugins = []
        for root, plugin_dirs, plugin_files in os.walk(PluginFolder):
            for plugin in plugin_dirs:
                modname = os.path.splitext(plugin)[0]
                if modname not in ['providers', self.Provider]:
                    continue
                sys.path.append(os.path.join(root, modname))
                try:
                    importlib.util.find_spec(modname).loader.load_module()
                except (AttributeError, FileNotFoundError, ImportError, NotImplementedError):
                    continue
                plugin_type = (os.path.split(root)[-1])
                plugins.append({'type': plugin_type, 'path': os.path.join(
                    root, plugin, self.MainModule)})
        return plugins
    #

    def path_import2(self, absolute_path):
        spec = importlib.util.spec_from_file_location(
            absolute_path, absolute_path)
        module = spec.loader.load_module(spec.name)
        return module
    #

    def activatePlugins(self, PluginFolder=None):
        PluginFolder = PluginFolder or self.PluginFolder
        plugin_objects = {
            'providers': []
        }
        for plugin_object in self.getPlugins(PluginFolder):
            plugin_instance = self.path_import2(plugin_object['path'])
            plugin_objects[plugin_object['type']].append(plugin_instance)
        return type('obj', (object,), plugin_objects)
