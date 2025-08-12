package controllers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/stretchr/testify/assert"
)

func setupTestController() *gin.Engine {
	gin.SetMode(gin.TestMode)

	// Mock minimal cache without real data
	core.VmaasAPI = vmaas.InitEmptyCache()

	router := gin.New()
	return router
}

func TestVersionHandlerCacheNotLoaded(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil // Simulate cache not loaded

	router.GET("/version", VersionHandler)
	req := createTestRequest("/version")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestDBChangeHandlerCacheNotLoaded(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil // Simulate cache not loaded

	router.GET("/dbchange", DBChangeHandler)
	req := createTestRequest("/dbchange")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestUpdatesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/updates/:package", UpdatesHandler)
	req := createTestRequest("/updates/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestUpdatesPostHandlerInvalidJSON(t *testing.T) {
	router := setupTestController()

	router.POST("/updates", UpdatesPostHandler)
	req := createTestRequestWithBody("POST", "/updates", "invalid json")
	w := performRequest(router, req)

	assert.Equal(t, 400, w.Code)
}

func TestUpdatesPostHandlerEmptyBody(t *testing.T) {
	router := setupTestController()

	router.POST("/updates", UpdatesPostHandler)
	req := createTestRequestWithBody("POST", "/updates", "")
	w := performRequest(router, req)

	assert.Equal(t, 400, w.Code)
}

func TestVulnerabilitiesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/vulnerabilities/:package", VulnerabilitiesHandler)
	req := createTestRequest("/vulnerabilities/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestCvesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/cves/:cve", CvesHandler)
	req := createTestRequest("/cves/CVE-2021-1234")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestErrataHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/errata/:erratum", ErrataHandler)
	req := createTestRequest("/errata/RHSA-2021:1234")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestReposHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/repos/:repo", ReposHandler)
	req := createTestRequest("/repos/rhel-8")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestPackagesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/packages/:nevra", PackagesHandler)
	req := createTestRequest("/packages/kernel-0:4.18.0-1.el8.x86_64")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestPkgListPostHandlerInvalidJSON(t *testing.T) {
	router := setupTestController()

	router.POST("/pkglist", PkgListPostHandler)
	req := createTestRequestWithBody("POST", "/pkglist", "invalid")
	w := performRequest(router, req)

	assert.Equal(t, 400, w.Code)
}

func TestPkgTreeHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/pkgtree/:package_name", PkgTreeHandler)
	req := createTestRequest("/pkgtree/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestPatchesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/patches/:nevra", PatchesHandler)
	req := createTestRequest("/patches/kernel-0:4.18.0-1.el8.x86_64")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestRPMPkgNamesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/package_names/rpms/:rpm", RPMPkgNamesHandler)
	req := createTestRequest("/package_names/rpms/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestSRPMPkgNamesHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/package_names/srpms/:srpm", SRPMPkgNamesHandler)
	req := createTestRequest("/package_names/srpms/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestOSHandlerWithoutCache(t *testing.T) {
	router := setupTestController()
	core.VmaasAPI = nil

	router.GET("/os/vulnerability/report", OSHandler)
	req := createTestRequest("/os/vulnerability/report")
	w := performRequest(router, req)

	assert.Equal(t, 503, w.Code)
}

func TestBindValidateJSONNilRequest(t *testing.T) {
	c, _ := gin.CreateTestContext(nil)
	err := bindValidateJSON(c, nil)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "nil vmaas request")
}

func TestBindValidateJSONModuleValidation(t *testing.T) {
	c, _ := gin.CreateTestContext(nil)

	// Create request with invalid module (missing required fields)
	req := &vmaas.Request{
		Modules: []vmaas.ModuleStreamPtrs{
			{Module: nil, Stream: &[]string{"test"}[0]}, // Missing module name
		},
	}

	// Mock the binding by setting the request in context
	c.Request = createTestRequestWithJSON("POST", "/test", req)

	err := bindValidateJSON(c, req)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "'module_name' is a required property")
}

func TestIsCacheLoadedTrue(t *testing.T) {
	c, _ := gin.CreateTestContext(nil)

	// Setup valid cache
	core.VmaasAPI = &vmaas.API{
		Cache: &vmaas.Cache{},
	}

	result := isCacheLoaded(c)
	assert.True(t, result)
}

func TestIsCacheLoadedFalse(t *testing.T) {
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	// No cache
	core.VmaasAPI = nil

	result := isCacheLoaded(c)
	assert.False(t, result)
	assert.Equal(t, 503, w.Code)
}

// Helper functions for creating test requests (using existing pattern from utils_test.go)
func createTestRequest(url string) *http.Request {
	return httptest.NewRequest("GET", url, nil)
}

func createTestRequestWithBody(method, url, body string) *http.Request {
	req := httptest.NewRequest(method, url, bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	return req
}

func createTestRequestWithJSON(method, url string, body interface{}) *http.Request {
	jsonBytes, _ := json.Marshal(body)
	req := httptest.NewRequest(method, url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")
	return req
}

func performRequest(r *gin.Engine, req *http.Request) *httptest.ResponseRecorder {
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	return w
}

// Cache loaded variants - these tests don't set core.VmaasAPI = nil
func TestVersionHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/version", VersionHandler)
	req := createTestRequest("/version")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestDBChangeHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/dbchange", DBChangeHandler)
	req := createTestRequest("/dbchange")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestUpdatesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/updates/:package", UpdatesHandler)
	req := createTestRequest("/updates/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestVulnerabilitiesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/vulnerabilities/:package", VulnerabilitiesHandler)
	req := createTestRequest("/vulnerabilities/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestCvesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/cves/:cve", CvesHandler)
	req := createTestRequest("/cves/CVE-2021-1234")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestErrataHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/errata/:erratum", ErrataHandler)
	req := createTestRequest("/errata/RHSA-2021:1234")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestReposHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/repos/:repo", ReposHandler)
	req := createTestRequest("/repos/rhel-8")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestPackagesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/packages/:nevra", PackagesHandler)
	req := createTestRequest("/packages/kernel-0:4.18.0-1.el8.x86_64")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestPkgTreeHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/pkgtree/:package_name", PkgTreeHandler)
	req := createTestRequest("/pkgtree/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestPatchesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/patches/:nevra", PatchesHandler)
	req := createTestRequest("/patches/kernel-0:4.18.0-1.el8.x86_64")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestRPMPkgNamesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/package_names/rpms/:rpm", RPMPkgNamesHandler)
	req := createTestRequest("/package_names/rpms/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestSRPMPkgNamesHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/package_names/srpms/:srpm", SRPMPkgNamesHandler)
	req := createTestRequest("/package_names/srpms/kernel")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}

func TestOSHandlerCacheLoaded(t *testing.T) {
	router := setupTestController()
	// core.VmaasAPI remains set (cache loaded)

	router.GET("/os/vulnerability/report", OSHandler)
	req := createTestRequest("/os/vulnerability/report")
	w := performRequest(router, req)

	assert.Equal(t, 200, w.Code)
}
