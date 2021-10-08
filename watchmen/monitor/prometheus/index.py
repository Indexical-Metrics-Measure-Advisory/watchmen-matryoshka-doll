from starlette_prometheus import metrics, PrometheusMiddleware


def init_prometheus_monitor(app):
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics/", metrics)

