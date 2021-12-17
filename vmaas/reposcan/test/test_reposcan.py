"""Reposcan overall test."""

import os

from http import HTTPStatus
from vmaas.reposcan.test.test_case import FlaskTestCase
from vmaas.reposcan.reposcan import PKGTREE_FILE


class TestReposcanApp(FlaskTestCase):
    """Reposcan overall test."""

    def test_monitoring_health(self):
        """Test monitoring health endpoint."""
        resp = self.fetch('/api/v1/monitoring/health', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.status)

    def test_version(self):
        """Test version endpoint."""
        resp = self.fetch('/api/v1/version', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.status)

    def test_add_repo_1(self):
        """Test add repo request."""
        body = """[{
           "products": {
             "Testing Repo": {
               "content_sets": {
                 "testing-repo-name": {
                   "name": "Testing repo desc",
                   "baseurl": "http://localhost:8888/$releasever/$basearch/",
                   "releasever": ["Server"],
                   "basearch": ["Arch"]
                 }
               }
             }
           },
           "entitlement_cert": {"name": "a", "ca_cert": "b", "cert": "c", "key": "d"}
        }]"""

        resp = self.fetch('/api/v1/repos', method='POST', data=body)
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertEqual({"msg": "Import repositories task started.", "success": True}, resp.body)
        resp = self.fetch('/api/v1/task/cancel', method='PUT', data=body)

    def test_add_repo_1_with_certs(self):
        """Test_add_repo - with certs and keys"""

        os.environ["RHSM-CDN-CA"] = "testRHSM-CDN-CA"
        os.environ["RHSM-CDN-CERT"] = "testRHSM-CDN-CERT"
        os.environ["RHSM-CDN-KEY"] = "testRHSM-CDN-KEY"

        body = """[{
           "products": {
             "Testing Repo": {
               "content_sets": {
                 "testing-repo-name": {
                   "name": "Testing repo desc",
                   "baseurl": "http://localhost:8888/$releasever/$basearch/",
                   "releasever": ["Server"],
                   "basearch": ["Arch"]
                 }
               }
             }
           },
           "entitlement_cert": {
              "name": "RHSM-CDN",
              "ca_cert": "$RHSM-CDN-CA",  
              "cert": "$RHSM-CDN-CERT",  
              "key": "$RHSM-CDN-KEY"
            }
        }]"""

        resp = self.fetch('/api/v1/repos', method='POST', data=body)
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertEqual({"msg": "Import repositories task started.", "success": True}, resp.body)
        resp = self.fetch('/api/v1/task/cancel', method='PUT', data=body)

    def test_add_repo_2(self):
        """Test add repo - bad request."""
        body = """[{"wrong_key: {}"}]"""
        resp = self.fetch('/api/v1/repos', method='POST', data=body)
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.status)

    def test_delete_repo(self):
        """Test delete repo endpoint."""
        resp = self.fetch('/api/v1/repos/myrepo', method='DELETE')
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_all(self):
        """Test sync all endpoint."""
        resp = self.fetch('/api/v1/sync', method='PUT', data="{}")
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_repo(self):
        """Test sync repo endpoint."""
        resp = self.fetch('/api/v1/sync/repo', method='PUT', data="{}")
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_cvemap(self):
        """Test sync cvemap endpoint."""
        resp = self.fetch('/api/v1/sync/cvemap', method='PUT', data="{}")
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_export_pkgtree(self):
        """Test export_pkgtree endpoint."""
        resp = self.fetch('/api/v1/export/pkgtree', method='PUT', data="{}")
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_export_dump(self):
        """Test export_dump endpoint."""
        resp = self.fetch('/api/v1/export/dump', method='PUT', data="{}")
        self.assertTrue(resp.status in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_pkgtree(self):
        """Test pkgtree endpoint."""
        os.system('rm -f %s' % PKGTREE_FILE)  # Remove pkgtree file if exists
        resp = self.fetch('/api/v1/pkgtree', method='GET')
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)
        assert resp.data == b"\"Package Tree file not found.  Has it been generated?\"\n"

    def test_task_cancel(self):
        """Test cancel task."""
        resp = self.fetch('/api/v1/task/cancel', method='PUT', data="{}")
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertEqual({"running": False, "task_type": None}, resp.body)

    def test_task_status(self):
        """Test get status request."""
        resp = self.fetch('/api/v1/task/status', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertEqual({"running": False, "task_type": None}, resp.body)

    def test_metrics(self):
        """Test metrics endpoint."""
        resp = self.fetch('/metrics', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.status)
