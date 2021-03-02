from watchmen.plugin.util.index import find_plugin_func


def run_plugin(factor_type,value):
    plugin = find_plugin_func(factor_type)
    if plugin is None:
        return None
    else:
        return plugin.run(value)


# TODO init plugin system
def init():
    pass