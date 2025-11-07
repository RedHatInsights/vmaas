package controllers

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/stretchr/testify/assert"
)

func mockPOST(c *gin.Context, body json.RawMessage) {
	c.Request = &http.Request{
		Header: make(http.Header),
	}
	c.Request.Method = "POST"
	c.Request.Header.Set("Content-Type", "application/json")
	c.Request.Body = io.NopCloser(bytes.NewBuffer(body))
}

type bindTest struct {
	name    string
	request *vmaas.Request
	body    json.RawMessage
	test    func(*testing.T, error, *vmaas.Request)
}

func testBindJSON(t *testing.T, test bindTest) {
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	mockPOST(c, test.body)
	err := bindValidateJSON(c, test.request)
	test.test(t, err, test.request)
}

func TestBindValidateJSON(t *testing.T) {
	request := vmaas.Request{}
	tests := []bindTest{
		{"empty_request", &request, nil, func(t *testing.T, err error, _ *vmaas.Request) { assert.Error(t, err) }},
		{
			"missing_module_name", &request, []byte(`{"modules_list": ["module_stream": "rhel"}]}`),
			func(t *testing.T, err error, _ *vmaas.Request) { assert.Error(t, err) },
		},
		{
			"missing_module_stream", &request, []byte(`{"modules_list": [{"module_name": "virt"]}`),
			func(t *testing.T, err error, _ *vmaas.Request) { assert.Error(t, err) },
		},
		{
			"module", &request, []byte(`{"modules_list": [{"module_name": "virt", "module_stream": "rhel"}]}`),
			func(t *testing.T, err error, _ *vmaas.Request) { assert.NoError(t, err) },
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			testBindJSON(t, test)
		})
	}
}

func TestBindValidateJSONInvalidDateFormat(t *testing.T) {
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	body := []byte(`{"modified_since": "2024-11-01"}`)
	mockPOST(c, body)

	req := vmaas.PkgListRequest{}
	err := bindValidateJSON(c, &req)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "wrong date format")
	assert.Contains(t, err.Error(), "2024-11-01")
}
