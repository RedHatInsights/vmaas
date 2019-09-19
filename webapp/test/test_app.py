"""Webapp api test."""

# pylint: disable=redefined-outer-name

from http import HTTPStatus

from test import yaml_cache
import pytest

from app import create_app, BaseHandler, load_cache_to_apis



@pytest.fixture()
async def server(aiohttp_server):
    """Setup testing app."""
    app = create_app()
    BaseHandler.db_cache = yaml_cache.load_test_cache()
    load_cache_to_apis()
    return await aiohttp_server(app.app)


@pytest.fixture()
async def client(server, aiohttp_client):
    """Setup testing client"""
    return await aiohttp_client(server)


# pylint: disable=attribute-defined-outside-init
class BaseCase():
    """Class implementing utility methods and providing fixtures"""

    @pytest.fixture(autouse=True)
    def _set_client(self, client):
        """Assign local variable to client"""
        self.client = client

    async def fetch(self, path, **kwargs):
        """Fetch method for vulnerability API."""
        headers = kwargs.get("headers") or {}
        headers["Authorization"] = "token 0000000"
        kwargs["headers"] = headers
        if 'data' in kwargs or 'json' in kwargs:
            headers.update({'Content-type': 'application/json'})
        method = kwargs.get('method', 'get')
        del kwargs['method']
        if method.upper() == 'PATCH':
            response = self.client.patch(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'POST':
            response = self.client.post(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'PUT':
            response = self.client.put(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'DELETE':
            response = self.client.delete(path, **kwargs)  # pylint: disable=no-member
        else:
            response = self.client.get(path, **kwargs)  # pylint: disable=no-member

        response = await response
        response.body = await response.text()
        return response


@pytest.mark.usefixtures('client', '_set_client')
class TestWebappPosts(BaseCase):
    """Webapp overall test."""

    async def test_updates_post_1(self):
        """Test updates post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = await self.fetch('/api/v1/updates', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"update_list": {"my-pkg-1.1.0'

    async def test_updates_post_2_short(self):
        """Test updates post endpoint."""
        body = """{"package_list": []}"""
        resp = await self.fetch('/api/v1/updates', method='POST', data=body)
        assert HTTPStatus.BAD_REQUEST == resp.status
        assert resp.body[:32] == '"package_list : [] is too short"'

    async def test_updates_v2_post_1(self):
        """Test updates post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = await self.fetch('/api/v2/updates', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"update_list": {"my-pkg-1.1.0'

    async def test_cves_post_1(self):
        """Test cves post endpoint."""
        body = """{"cve_list": [".*"]}"""
        resp = await self.fetch('/api/v1/cves', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"cve_list": {"CVE-2014-1545":'

    async def test_repos_post_1(self):
        """Test repos post endpoint."""
        body = """{"repository_list": [".*"]}"""
        resp = await self.fetch('/api/v1/repos', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"repository_list": {"rhel-7-s'

    async def test_errata_post_1(self):
        """Test errata post endpoint."""
        body = """{"errata_list": [".*"]}"""
        resp = await self.fetch('/api/v1/errata', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"errata_list": {"RHBA-2015:03'

    async def test_packages_post_1(self):
        """Test packages post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = await self.fetch('/api/v1/packages', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"package_list": {"my-pkg-1.1.'

    async def test_vulnerabilities_post_1(self):
        """Test vulnerabilities post endpoint."""
        body = """{"package_list": ["my-pkg-1.1.0-1.el8.i686"]}"""
        resp = await self.fetch('/api/v1/vulnerabilities', method='POST', data=body)
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"cve_list": ["CVE-2014-1545"]'


@pytest.mark.usefixtures('client')
class TestWebappGets(BaseCase):
    """Webapp overall test."""

    async def test_updates_get(self):
        """Test updates post endpoint."""
        resp = await self.fetch('/api/v1/updates/my-pkg-1.1.0-1.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"update_list": {"my-pkg-1.1.0'

    async def test_updates_get_tilda(self):
        """Test updates get endpoint."""
        resp = await self.fetch('/api/v1/updates/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:40] == '{"update_list": {"my-pkg-1.1.0-1~beta.el'

    async def test_updates_get_tilda_escaped(self):
        """Test updates get endpoint."""
        resp = await self.fetch('/api/v1/updates/my-pkg-1.1.0-1%7Ebeta.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:40] == '{"update_list": {"my-pkg-1.1.0-1~beta.el'

    async def test_updates_get_caret(self):
        """Test updates get endpoint."""
        resp = await self.fetch('/api/v1/updates/my-pkg-1.1.0-1^.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:50] == '{"update_list": {"my-pkg-1.1.0-1^.el8.i686": {}}}'

    async def test_updates_v2_get(self):
        """Test updates post endpoint."""
        resp = await self.fetch('/api/v2/updates/my-pkg-1.1.0-1.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"update_list": {"my-pkg-1.1.0'

    async def test_cves_get_1(self):
        """Test cves get endpoint."""
        resp = await self.fetch('/api/v1/cves/.*', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"cve_list": {"CVE-2014-1545":'

    async def test_repos_get_1(self):
        """Test repos get endpoint."""
        resp = await self.fetch('/api/v1/repos/.*', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"repository_list": {"rhel-7-s'

    async def test_errata_get_1(self):
        """Test errata get endpoint."""
        resp = await self.fetch('/api/v1/errata/.*', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"errata_list": {"RHBA-2015:03'

    async def test_packages_get_1(self):
        """Test packages get endpoint."""
        resp = await self.fetch('/api/v1/packages/my-pkg-1.1.0-1.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"package_list": {"my-pkg-1.1.'

    async def test_packages_get_2_tilda(self):
        """Test packages get endpoint."""
        resp = await self.fetch('/api/v1/packages/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"package_list": {"my-pkg-1.1.'

    async def test_packages_get_3_caret(self):
        """Test packages get endpoint."""
        resp = await self.fetch('/api/v1/packages/my-pkg-1.1.0-1^.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"package_list": {"my-pkg-1.1.'

    async def test_dbchange(self):
        """Test dbchange endpoint."""
        resp = await self.fetch('/api/v1/dbchange', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"cve_changes": "2019-03-07T09'

    async def test_vuln_get_1(self):
        """Test vulnerabilities get endpoint."""
        resp = await self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == '{"cve_list": ["CVE-2014-1545"]'

    async def test_vuln_get_2_tilda(self):
        """Test vulnerabilities get endpoint."""
        resp = await self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1~beta.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body == '{"cve_list": []}'

    async def test_vuln_get_3_caret(self):
        """Test vulnerabilities get endpoint."""
        resp = await self.fetch('/api/v1/vulnerabilities/my-pkg-1.1.0-1^.el8.i686', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body == '{"cve_list": []}'


@pytest.mark.usefixtures('client')
class TestWebappSupportMethods(BaseCase):
    """Webapp overall test."""

    async def test_monitoring_health(self):
        """Test monitoring health endpoint."""
        resp = await self.fetch('/api/v1/monitoring/health', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body == ''

    async def test_apispec(self):
        """Test apispec endpoint."""
        resp = await self.fetch('/api/v1/apispec', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == """{
  "openapi": "3.0.0",
  "inf"""

    async def test_version(self):
        """Test version endpoint."""
        resp = await self.fetch('/api/v1/version', method='GET')
        assert HTTPStatus.OK == resp.status
        assert resp.body[:30] == 'unknown'

    async def test_metrics(self):
        """Test metrics endpoint."""
        resp = await self.fetch('/metrics', method='GET')
        assert HTTPStatus.OK == resp.status
