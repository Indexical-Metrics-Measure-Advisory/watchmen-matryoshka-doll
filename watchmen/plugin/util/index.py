# import importlib
# import logging
#
# PLUGIN__MODULE_PATH = "watchmen.plugin."
#
# log = logging.getLogger("app." + __name__)
#
#
# def find_plugin_func(plugin_type):
#     try:
#         plugin = importlib.import_module(PLUGIN__MODULE_PATH + plugin_type)
#         # print(plugin)
#         return plugin
#     except:
#         log.debug("can't find plugin {0}".format(plugin_type))
#         return None
