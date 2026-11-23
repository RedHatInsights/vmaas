"""Tests for repository metadata downloads."""
import ssl
from queue import Queue
from unittest.mock import Mock

import certifi

from vmaas.reposcan.download.downloader import FileDownloadThread, NonStrictTLSAdapter


def test_tls_adapter_validates_cert():
    """Custom CA downloads retain certificate validation but accept legacy extensions."""
    adapter = NonStrictTLSAdapter(certifi.where())

    assert adapter.ssl_context.verify_mode == ssl.CERT_REQUIRED
    assert adapter.ssl_context.check_hostname
    assert not adapter.ssl_context.verify_flags & ssl.VERIFY_X509_STRICT


def test_ca_bundle_reuses_session():
    """Downloads sharing a CA bundle use the same tailored HTTPS session."""
    thread = FileDownloadThread(Queue(), Mock(), Mock())

    session = thread.get_session(certifi.where())

    assert session is thread.get_session(certifi.where())
    assert session is not thread.session
    assert isinstance(session.adapters["https://"], NonStrictTLSAdapter)

    thread.session.close()
    session.close()
