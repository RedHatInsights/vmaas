"""Reposcan overall test."""

import os

from http import HTTPStatus

from tornado.testing import AsyncHTTPTestCase

import reposcan


class TestReposcanApp(AsyncHTTPTestCase):
    """Reposcan overall test."""

    def get_app(self):
        """Setup testing app."""
        return reposcan.ReposcanApplication()

    def test_monitoring_health(self):
        """Test monitoring health endpoint."""
        resp = self.fetch('/api/v1/monitoring/health', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)

    def test_apispec(self):
        """Test apispec endpoint."""
        resp = self.fetch('/api/v1/apispec', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)

    def test_version(self):
        """Test version endpoint."""
        resp = self.fetch('/api/v1/version', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)

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

        resp = self.fetch('/api/v1/repos', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(b'{"msg": "Import repositories task started.", "success": true}', resp.body)
        resp = self.fetch('/api/v1/task/cancel', method='PUT', body=body)

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

        resp = self.fetch('/api/v1/repos', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(b'{"msg": "Import repositories task started.", "success": true}', resp.body)
        resp = self.fetch('/api/v1/task/cancel', method='PUT', body=body)

    def test_add_repo_2(self):
        """Test add repo - bad request."""
        body = """[{"wrong_key: {}"}]"""
        resp = self.fetch('/api/v1/repos', method='POST', body=body)
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.code)

    def test_delete_repo(self):
        """Test delete repo endpoint."""
        resp = self.fetch('/api/v1/repos/myrepo', method='DELETE')
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_all(self):
        """Test sync all endpoint."""
        resp = self.fetch('/api/v1/sync', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_repo(self):
        """Test sync repo endpoint."""
        resp = self.fetch('/api/v1/sync/repo', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_cve(self):
        """Test sync cve endpoint."""
        resp = self.fetch('/api/v1/sync/cve', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_cvemap(self):
        """Test sync cvemap endpoint."""
        resp = self.fetch('/api/v1/sync/cvemap', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_sync_pkgtree(self):
        """Test sync_pkgtree endpoint."""
        resp = self.fetch('/api/v1/sync/pkgtree', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_export(self):
        """Test export endpoint."""
        resp = self.fetch('/api/v1/export', method='PUT', body="{}")
        self.assertTrue(resp.code in [HTTPStatus.OK, HTTPStatus.TOO_MANY_REQUESTS])

    def test_pkgtree(self):
        """Test pkgtree endpoint."""
        resp = self.fetch('/api/v1/pkgtree', method='GET')
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.code)
        self.assertEqual("Package Tree file not found.  Has it been generated?", resp.error.message)

    def test_task_status(self):
        """Test get status request."""
        resp = self.fetch('/api/v1/task/status', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(b'{"running": false, "task_type": null}', resp.body)

    def test_task_cancel(self):
        """Test cancel task."""
        resp = self.fetch('/api/v1/task/cancel', method='PUT', body="{}")
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(b'{"running": false, "task_type": null}', resp.body)

    def test_metrics(self):
        """Test metrics endpoint."""
        resp = self.fetch('/metrics', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
