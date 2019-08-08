"""Webapp api test."""

from http import HTTPStatus

from test import yaml_cache
from tornado.testing import AsyncHTTPTestCase

import app


class TestWebappPosts(AsyncHTTPTestCase):
    """Webapp overall test."""

    def get_app(self):
        """Setup testing app."""
        app.BaseHandler.db_cache = yaml_cache.load_test_cache()
        app.load_cache_to_apis()
        return app.Application()

    def test_updates_post_1(self):
        """Test updates post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = self.fetch('/api/v1/updates', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"update_list": {"my-pkg-1.1.0')

    def test_updates_post_2_short(self):
        """Test updates post endpoint."""
        body = """{"package_list": []}"""
        resp = self.fetch('/api/v1/updates', method='POST', body=body)
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.code)
        self.assertEqual(resp.error.message, 'Bad Request')

    def test_updates_v2_post_1(self):
        """Test updates post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = self.fetch('/api/v2/updates', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"update_list": {"my-pkg-1.1.0')

    def test_cves_post_1(self):
        """Test cves post endpoint."""
        body = """{"cve_list": [".*"]}"""
        resp = self.fetch('/api/v1/cves', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"cve_list": {"CVE-2014-1545":')

    def test_repos_post_1(self):
        """Test repos post endpoint."""
        body = """{"repository_list": [".*"]}"""
        resp = self.fetch('/api/v1/repos', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"repository_list": {"rhel-7-s')

    def test_errata_post_1(self):
        """Test errata post endpoint."""
        body = """{"errata_list": [".*"]}"""
        resp = self.fetch('/api/v1/errata', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"errata_list": {"RHBA-2015:03')

    def test_packages_post_1(self):
        """Test packages post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = self.fetch('/api/v1/packages', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"package_list": {"my-pkg-1.1.')

    def test_vulnerabilities_post_1(self):
        """Test vulnerabilities post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = self.fetch('/api/v1/vulnerabilities', method='POST', body=body)
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"cve_list": ["CVE-2014-1545"]')


class TestWebappGets(AsyncHTTPTestCase):
    """Webapp overall test."""

    def get_app(self):
        """Setup testing app."""
        app.BaseHandler.db_cache = yaml_cache.load_test_cache()
        app.load_cache_to_apis()
        return app.Application()

    def test_updates_get(self):
        """Test updates post endpoint."""
        resp = self.fetch('/api/v1/updates/my-pkg-1.1.0-1.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"update_list": {"my-pkg-1.1.0')

    def test_updates_get_tilda(self):
        """Test updates get endpoint."""
        resp = self.fetch('/api/v1/updates/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:40], b'{"update_list": {"my-pkg-1.1.0-1~beta.el')

    def test_updates_get_tilda_escaped(self):
        """Test updates get endpoint."""
        resp = self.fetch('/api/v1/updates/my-pkg-1.1.0-1%7Ebeta.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:40], b'{"update_list": {"my-pkg-1.1.0-1~beta.el')

    def test_updates_get_caret(self):
        """Test updates get endpoint."""
        resp = self.fetch('/api/v1/updates/my-pkg-1.1.0-1^.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:50], b'{"update_list": {"my-pkg-1.1.0-1^.el8.i686": {}}}')

    def test_updates_v2_get(self):
        """Test updates post endpoint."""
        resp = self.fetch('/api/v2/updates/my-pkg-1.1.0-1.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"update_list": {"my-pkg-1.1.0')

    def test_cves_get_1(self):
        """Test cves get endpoint."""
        resp = self.fetch('/api/v1/cves/.*', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"cve_list": {"CVE-2014-1545":')

    def test_repos_get_1(self):
        """Test repos get endpoint."""
        resp = self.fetch('/api/v1/repos/.*', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"repository_list": {"rhel-7-s')

    def test_errata_get_1(self):
        """Test errata get endpoint."""
        resp = self.fetch('/api/v1/errata/.*', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"errata_list": {"RHBA-2015:03')

    def test_packages_get_1(self):
        """Test packages get endpoint."""
        resp = self.fetch('/api/v1/packages/my-pkg-1.1.0-1.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"package_list": {"my-pkg-1.1.')

    def test_packages_get_2_tilda(self):
        """Test packages get endpoint."""
        resp = self.fetch('/api/v1/packages/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"package_list": {"my-pkg-1.1.')

    def test_packages_get_3_caret(self):
        """Test packages get endpoint."""
        resp = self.fetch('/api/v1/packages/my-pkg-1.1.0-1^.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"package_list": {"my-pkg-1.1.')

    def test_dbchange(self):
        """Test dbchange endpoint."""
        resp = self.fetch('/api/v1/dbchange', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"cve_changes": "2019-03-07T09')

    def test_vuln_get_1(self):
        """Test vulnerabilities get endpoint."""
        resp = self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"cve_list": ["CVE-2014-1545"]')

    def test_vuln_get_2_tilda(self):
        """Test vulnerabilities get endpoint."""
        resp = self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body, b'{"cve_list": []}')

    def test_vuln_get_3_caret(self):
        """Test vulnerabilities get endpoint."""
        resp = self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1^.el8.i686', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body, b'{"cve_list": []}')


class TestWebappSupportMethods(AsyncHTTPTestCase):
    """Webapp overall test."""

    def get_app(self):
        """Setup testing app."""
        return app.Application()

    def test_monitoring_health(self):
        """Test monitoring health endpoint."""
        resp = self.fetch('/api/v1/monitoring/health', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body, b'')

    def test_apispec(self):
        """Test apispec endpoint."""
        resp = self.fetch('/api/v1/apispec', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'{"info": {"title": "VMaaS Weba')

    def test_version(self):
        """Test version endpoint."""
        resp = self.fetch('/api/v1/version', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
        self.assertEqual(resp.body[:30], b'unknown')

    def test_metrics(self):
        """Test metrics endpoint."""
        resp = self.fetch('/metrics', method='GET')
        self.assertEqual(HTTPStatus.OK, resp.code)
