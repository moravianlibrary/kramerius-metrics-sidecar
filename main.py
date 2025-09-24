import threading
import time
from typing import List, Optional

import typer
from kramerius import KrameriusClient, KrameriusConfig, ProcessState
from prometheus_client import Gauge, start_http_server

app = typer.Typer(help="Kramerius Metrics Sidecar")

# Prometheus Gauges for process states
process_state_gauges = {
    state: Gauge(
        f"kramerius_process_{state.value}_count",
        f"Number of processes in {state.value} state",
    )
    for state in ProcessState
}


def poll_process_states(
    client: KrameriusClient, states: List[ProcessState], interval: int
):
    while True:
        for state in states:
            count = client.Processing.get_count_by_state(state)
            process_state_gauges[state].set(count)
        time.sleep(interval)


@app.command()
def main(
    host: Optional[str] = typer.Option(
        None, envvar="K7_HOST", help="Kramerius server host"
    ),
    keycloak_host: Optional[str] = typer.Option(
        None, envvar="K7_KEYCLOAK_HOST", help="Keycloak server host"
    ),
    client_id: Optional[str] = typer.Option(
        None, envvar="K7_CLIENT_ID", help="Keycloak client ID"
    ),
    client_secret: Optional[str] = typer.Option(
        None, envvar="K7_CLIENT_SECRET", help="Keycloak client secret"
    ),
    username: Optional[str] = typer.Option(
        None,
        envvar="K7_USERNAME",
        help="Username for authentication with Keycloak",
    ),
    password: Optional[str] = typer.Option(
        None,
        envvar="K7_PASSWORD",
        help="Password for authentication with Keycloak",
    ),
    timeout: Optional[int] = typer.Option(
        30, envvar="K7_TIMEOUT", help="Request timeout in seconds"
    ),
    max_retries: Optional[int] = typer.Option(
        5,
        envvar="K7_MAX_RETRIES",
        help="Maximum number of retries for failed requests",
    ),
    retry_timeout: Optional[int] = typer.Option(
        30,
        envvar="K7_RETRY_TIMEOUT",
        help="Timeout between retries in seconds",
    ),
    metrics_port: int = typer.Option(
        8000,
        envvar="METRICS_PORT",
        help="Port to expose Prometheus metrics on",
    ),
    metrics_poll_interval: int = typer.Option(
        30,
        envvar="METRICS_POLL_INTERVAL",
        help="Interval in seconds to poll Kramerius for process states",
    ),
    expose_metrics_for_states: List[ProcessState] = typer.Option(
        [ProcessState.Failed, ProcessState.Warning],
        envvar="EXPOSE_METRICS_FOR_STATES",
        help="List of process states to expose metrics for",
    ),
) -> KrameriusClient:
    # Kramerius Client
    client = KrameriusClient(
        KrameriusConfig(
            host=host,
            keycloak_host=keycloak_host,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            timeout=timeout,
            max_retries=max_retries,
            retry_timeout=retry_timeout,
        )
    )

    # Check that at least one metric is to be exposed
    if not expose_metrics_for_states:
        raise typer.BadParameter("At least one metric should be exposed")

    # Test connection
    client.Processing.get_count_by_state(ProcessState.Failed)

    # Start Prometheus metrics server
    start_http_server(metrics_port)
    typer.echo(
        f"Prometheus metrics exposed at http://0.0.0.0:{metrics_port}/metrics"
    )

    # Start states metrics polling thread
    poll_thread = threading.Thread(
        target=poll_process_states,
        args=(client, expose_metrics_for_states, metrics_poll_interval),
    )
    poll_thread.daemon = True
    poll_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(metrics_poll_interval)


if __name__ == "__main__":
    app()
