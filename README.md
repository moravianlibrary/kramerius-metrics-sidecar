# Kramerius Metrics Sidecar

The **Kramerius Metrics Sidecar** Docker image collects process state metrics from a Kramerius instance and exposes them for Prometheus.

## Running the Container

Run the container alongside your Kramerius container and let it scrape the metrics. If both containers run on the same machine, the recommended approach is to set up access to the endpoint `/api/admin/v7.0/processes/batches` by using `DefaultIPAddressFilter` for the action `a_process_read`.

### Environment Variables

| Variable                    | Default        | Description                                                  |
| --------------------------- | -------------- | ------------------------------------------------------------ |
| `K7_HOST`                   | –              | Kramerius server base URL                                    |
| `K7_KEYCLOAK_HOST`          | –              | Keycloak server URL                                          |
| `K7_CLIENT_ID`              | –              | Keycloak client ID                                           |
| `K7_CLIENT_SECRET`          | –              | Keycloak client secret                                       |
| `K7_USERNAME`               | –              | Keycloak username                                            |
| `K7_PASSWORD`               | –              | Keycloak password                                            |
| `K7_TIMEOUT`                | 30             | HTTP request timeout (seconds)                               |
| `K7_MAX_RETRIES`            | 5              | Maximum number of retries for failed requests                |
| `K7_RETRY_TIMEOUT`          | 30             | Time between retries (seconds)                               |
| `METRICS_PORT`              | 8000           | Port to expose Prometheus metrics                            |
| `METRICS_POLL_INTERVAL`     | 30             | Interval in seconds to poll Kramerius                        |
| `EXPOSE_METRICS_FOR_STATES` | Failed,Warning | Comma-separated list of process states to expose metrics for |

---

### Accessing Metrics

Prometheus can scrape metrics at:

```
http://<container-host>:<METRICS_PORT>/metrics
```

Example metrics:

```
kramerius_process_Failed_count 5
kramerius_process_Warning_count 2
```

### Integrating with Prometheus and Grafana

1. **Prometheus**: Add a scrape job to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'kramerius_metrics_sidecar'
    static_configs:
      - targets: ['<container-host>:8000']
```

2. **Grafana**:

   * Import metrics from Prometheus.
   * Create dashboards or alerts based on `kramerius_process_<STATE>_count` metrics.
   * Example alert: Trigger if `kramerius_process_Failed_count > 0`.

This setup allows you to monitor Kramerius processes in near real-time and trigger alerts when processes fail or enter warning states.
