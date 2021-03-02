from watchmen.plugin.langid_detect import detect
from watchmen.plugin.util.index import find_plugin_func


def build_plugin_name(language):
    return "address_" + language


def load_address_plugin(language):
    plugin_name = build_plugin_name(language)
    plugin = find_plugin_func(plugin_name)
    return plugin


def run(address):
    language = detect(address)
    address_plugin = load_address_plugin(language[0])
    if address_plugin is None:
        return address
    else:
        return address_plugin.run(address)
