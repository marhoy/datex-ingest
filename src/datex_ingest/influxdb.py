"""InfluxDB related stuff."""

from typing import List

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from datex_ingest import config
from datex_ingest.datex_api import Segment, TravelTimeMeasurement


def write_measurements(
    measurements: List[TravelTimeMeasurement], segments: List[Segment]
) -> None:
    """Write a list of DATEX measurements to InfluxDB."""
    segment_mapping = {segment.id: segment.name for segment in segments}

    client = InfluxDBClient(
        url=config.INFLUX_URL,
        token=config.INFLUX_TOKEN.get_secret_value(),
        org=config.INFLUX_ORG,
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # List of Points containting the travel_time for each segment.
    points = [
        Point("travel_time")
        .tag("segment", m.segment_id)
        .tag("segment_name", segment_mapping[m.segment_id])
        .field("value", m.travel_time)
        .time(m.timestamp)
        for m in measurements
    ]

    # List of Points containting the freeflow_time for each segment.
    points.extend(
        [
            Point("freeflow_time")
            .tag("segment", m.segment_id)
            .tag("segment_name", segment_mapping[m.segment_id])
            .field("value", m.freeflow_time)
            .time(m.timestamp)
            for m in measurements
        ]
    )

    write_api.write(bucket=config.INFLUX_BUCKET, record=points)
