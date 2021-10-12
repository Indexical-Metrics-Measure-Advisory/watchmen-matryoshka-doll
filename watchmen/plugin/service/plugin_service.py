# import logging
#
# from watchmen.plugin.util.index import find_plugin_func
#
# log = logging.getLogger("app." + __name__)
#
#
# # @lru_cache(maxsize=16)
# def run_plugin(factor_type, value):
#     try:
#         # TODO custom plugin from ext folder
#         plugin = find_plugin_func(factor_type)
#         if plugin is None:
#             return None
#         else:
#             return plugin.run(value)
#     except Exception as e:
#         log.exception(e)
#         return None
#
#
# # TODO init plugin system
# def init():
#     pass
