import importlib

PLUGIN__MODULE_PATH = "watchmen.plugin."


def find_plugin_func(plugin_type):
    plugin = importlib.import_module(PLUGIN__MODULE_PATH + plugin_type)
    return plugin


def build_plugin_name(language):
    return "address_" + language


def load_address_plugin(language):
    try:
        plugin_name = build_plugin_name(language)
        plugin = find_plugin_func(plugin_name)
        return plugin
    except:
        print("no such plugin")
        return None
