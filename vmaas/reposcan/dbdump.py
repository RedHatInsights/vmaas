"""DbDump API implementation."""
import os
import subprocess

import starlette.responses

from vmaas.common.config import Config

CFG = Config()
FILENAME = "pgdump.sql.gz"
DUMP = f"/data/{FILENAME}"


class DbDumpAPI:
    """API class to work with dbdump."""

    @staticmethod
    def create():
        """Processes the dbdump get request."""
        os.environ["PGPASSWORD"] = CFG.db_pass
        ssl_args = f"sslrootcert={CFG.db_ssl_root_cert_path} sslmode={CFG.db_ssl_mode}"
        pg_dump = [
            "pg_dump",
            f"port={CFG.db_port} host={CFG.db_host} user={CFG.db_user} dbname={CFG.db_name} {ssl_args}",
        ]
        with open(DUMP, "w", encoding="utf-8") as out:
            with subprocess.Popen(pg_dump, stdout=subprocess.PIPE) as dump_process:
                with subprocess.Popen(["gzip"], stdin=dump_process.stdout, stdout=out) as gzip_process:
                    _, error = gzip_process.communicate()
                    if error:
                        raise RuntimeError(f"pg_dump exited with {error}")

    @staticmethod
    def download():
        """Download pg_dump"""
        if not os.path.exists(DUMP):
            return {"error": "pg_dump is not exported"}, 404, {"Content-type": "application/json"}
        return starlette.responses.FileResponse(DUMP, media_type="application/octet-stream", filename=FILENAME)
