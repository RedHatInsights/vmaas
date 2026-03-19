"""
Metrics that need refreshing in the main process
Updated at startup and after sync completes so they appear in the default registry
"""

import logging
from datetime import datetime
from typing import Optional, Set

import psycopg2
from OpenSSL import crypto

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler, init_db
from vmaas.reposcan.mnm import CERT_EXPIRATION_WARNING

EXPIRATION_WARNING_DAYS = 14

LOGGER = get_logger(__name__)


class _CertGaugeState:
    """Last exported cert_name labels (main process)"""

    tracked_names: Optional[Set[str]] = None


def check_cert_expiration(
    cert_name: str,
    cert_pem: Optional[str],
    logger: Optional[logging.Logger] = None,
) -> int:
    """Parse cert, update Prometheus gauge, return days until expiry (-1 if invalid/missing)"""
    if not cert_pem:
        days = -1
        CERT_EXPIRATION_WARNING.labels(cert_name=cert_name).set(days)
    else:
        try:
            loaded_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
            valid_to_dt = datetime.strptime(loaded_cert.get_notAfter().decode("utf-8"), "%Y%m%d%H%M%SZ")
            days = (valid_to_dt - datetime.utcnow()).days
            CERT_EXPIRATION_WARNING.labels(cert_name=cert_name).set(days)
        except (crypto.Error, ValueError):
            days = -1
            CERT_EXPIRATION_WARNING.labels(cert_name=cert_name).set(days)

    if logger is not None:
        if days <= 0:
            logger.error('Certificate %s expired!', cert_name if cert_name else 'None')
        elif days <= EXPIRATION_WARNING_DAYS:
            logger.warning('Certificate %s will expire in %s days!', cert_name, days)
        else:
            logger.info('Certificate %s will expire in %s days.', cert_name, days)

    return days


def update_cert_expiration_gauges():
    """Update cert expiration gauges from DB (certs in use by repos). Main process."""
    certs = {}

    try:
        init_db()
        cur = DatabaseHandler.get_connection().cursor()
        cur.execute("""
            SELECT DISTINCT c.name, c.cert FROM certificate c
            JOIN repo r ON r.certificate_id = c.id
            WHERE c.cert IS NOT NULL AND c.cert != ''
        """)
        for name, cert in cur.fetchall():
            certs[name] = cert
        cur.close()
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
        # DB not reachable
        LOGGER.warning("Cert expiration gauges: database unavailable (%s)", exc)
    except psycopg2.Error:
        LOGGER.exception("Cert expiration gauges: database error while loading certificates from DB")

    current_names = set(certs.keys())
    if _CertGaugeState.tracked_names is not None:
        for name in _CertGaugeState.tracked_names - current_names:
            CERT_EXPIRATION_WARNING.remove(name)
    _CertGaugeState.tracked_names = current_names

    for cert_name, cert_pem in certs.items():
        check_cert_expiration(cert_name, cert_pem)
