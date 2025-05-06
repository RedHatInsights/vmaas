"""
Module containing models for Release Graph objects.
"""

import hashlib
import json

from attr import define, field
from psycopg2.extras import Json


def graph_converter(graph: str | dict) -> Json:
    """Convert Graph string or dict (json) to psycopg.Json"""
    if isinstance(graph, dict):
        return Json(graph)
    return Json(json.loads(graph))


@define
class ReleaseGraph:
    """Release graph object."""

    name: str
    graph: Json = field(converter=graph_converter)
    checksum: str = field()

    @checksum.default
    def _checksum_factory(self) -> str:
        json_str = json.dumps(self.graph.adapted, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
