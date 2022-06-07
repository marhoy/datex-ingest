"""DATEX-related stuff."""

import datetime
from typing import List
from zoneinfo import ZoneInfo

import requests
from lxml import etree
from pydantic import BaseModel

from datex_ingest import config

TRAVEL_TIME_URL = "https://www.vegvesen.no/ws/no/vegvesen/veg/trafikkpublikasjon/reisetid/3/GetTravelTimeData"  # noqa: E501
LOCATION_URL = "https://www.vegvesen.no/ws/no/vegvesen/veg/trafikkpublikasjon/reisetid/3/GetPredefinedTravelTimeLocations"  # noqa: E501

XML_NS = {
    "rtd": "http://datex2.eu/schema/3/roadTrafficData",
    "lref": "http://datex2.eu/schema/3/locationReferencing",
    "cmn": "http://datex2.eu/schema/3/common",
}


class Segment(BaseModel):
    """Data class for road segment from DATEX."""

    id: int
    name: str


class TravelTimeMeasurement(BaseModel):
    """Data class for measurements from DATEX."""

    segment_id: int
    timestamp: datetime.datetime
    travel_time: int
    freeflow_time: int


def get_traveltime_data() -> List[TravelTimeMeasurement]:
    """Get measurements from DATEX API."""
    r = requests.get(
        TRAVEL_TIME_URL,
        auth=(config.DATEX_USERNAME, config.DATEX_PASSWORD.get_secret_value()),
    )
    tree = etree.fromstring(r.text)

    measurements = []
    # Start by finding nodes with a travelTime-measurement
    for node in tree.xpath("//rtd:travelTime/rtd:duration", namespaces=XML_NS):
        travel_time = int(node.text.split(".")[0])

        # Find the other values relative to the travelTime-node
        segment_id = int(node.xpath("../../..//@id")[0])

        # Return the end-of-period timestamp as UTC without seconds.
        timestamp = (
            datetime.datetime.fromisoformat(
                node.xpath("../..//cmn:endOfPeriod/text()", namespaces=XML_NS)[0]
            )
            .replace(microsecond=0)
            .astimezone(ZoneInfo("UTC"))
        )
        freeflow_time = int(
            node.xpath(
                "../../rtd:freeFlowTravelTime/rtd:duration/text()",
                namespaces=XML_NS,
            )[0].split(".")[0]
        )

        measurements.append(
            TravelTimeMeasurement(
                segment_id=segment_id,
                timestamp=timestamp,
                travel_time=travel_time,
                freeflow_time=freeflow_time,
            )
        )

    return measurements


def get_segments():
    """Get road segments from DATEX API."""
    r = requests.get(
        LOCATION_URL,
        auth=(config.DATEX_USERNAME, config.DATEX_PASSWORD.get_secret_value()),
    )
    tree = etree.fromstring(r.text)
    segments = []
    for segment in tree.xpath("//lref:predefinedLocationReference", namespaces=XML_NS):
        name = segment.xpath(
            "lref:predefinedLocationName/cmn:values/cmn:value/text()", namespaces=XML_NS
        )[0]
        segments.append(Segment(id=segment.get("id"), name=name))

    return segments
