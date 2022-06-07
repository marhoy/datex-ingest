from typing import List
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from datex_ingest import config
from datex_ingest.datex_api import TravelTimeMeasurement


def write_measurements(measurements: List[TravelTimeMeasurement]) -> None:
    client = InfluxDBClient(
        url=config.INFLUX_URL,
        token=config.INFLUX_TOKEN.get_secret_value(),
        org=config.INFLUX_ORG,
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    points = [
        Point("travel_time")
        .tag("segment", m.segment_id)
        .field("travel_time", m.travel_time)
        .field("freeflow_time", m.freeflow_time)
        .time(m.timestamp)
        for m in measurements
    ]

    write_api.write(bucket=config.INFLUX_BUCKET, record=points)
