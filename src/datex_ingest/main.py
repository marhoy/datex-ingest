"""CLI related stuff."""
import datetime

from datex_ingest import datex_api, influxdb


def main() -> None:
    """CLI entrypoint."""
    measurements = datex_api.get_traveltime_data()
    segments = datex_api.get_segments()
    influxdb.write_measurements(measurements, segments)

    now = datetime.datetime.now().replace(microsecond=0)
    print(
        f"{now}: Wrote {len(measurements)} segments with "
        f"timestamp {measurements[0].timestamp}."
    )
