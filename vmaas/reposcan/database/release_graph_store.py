"""
Module containing class for fetching/importing RHEL release graph metadata from/into database.
"""

from psycopg2.extras import execute_values

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler
from vmaas.reposcan.mnm import RELEASE_GRAPH_FAILED_IMPORT
from vmaas.reposcan.redhatreleasegraph.modeling import ReleaseGraph


class ReleaseGraphStore:
    """Class providing interface for storing release graph metadata."""

    def __init__(self, release_graphs: dict[str, ReleaseGraph]) -> None:
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()
        self.release_graphs = release_graphs

    def store(self) -> None:
        """Store release graphs into DB"""
        cur = self.conn.cursor()
        graphs_db: dict[str, ReleaseGraph] = {}
        try:
            cur.execute("SELECT name, graph, checksum FROM release_graph")
            for row in cur.fetchall():
                graphs_db[row[0]] = ReleaseGraph(row[0], row[1], row[2])

            to_insert = []
            to_update = []
            for name, graph in self.release_graphs.items():
                if name not in graphs_db:
                    to_insert.append((graph.name, graph.graph, graph.checksum))
                    continue
                if graphs_db[name].checksum != graph.checksum:
                    to_update.append((graph.name, graph.graph, graph.checksum))

            if to_insert:
                execute_values(
                    cur,
                    "INSERT INTO release_graph (name, graph, checksum) VALUES %s",
                    to_insert,
                )
            if to_update:
                execute_values(
                    cur,
                    """
                        UPDATE release_graph AS old
                        SET graph = new.graph::jsonb, checksum = new.checksum
                        FROM (VALUES %s) AS new(name, graph, checksum)
                        WHERE old.name = new.name
                    """,
                    to_update,
                )
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            RELEASE_GRAPH_FAILED_IMPORT.inc()
            self.logger.exception("%s: ", "Failed to import release graph to DB")
            self.conn.rollback()
        finally:
            cur.close()
