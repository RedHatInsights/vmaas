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
		{"use_csaf_default", &vmaas.Request{UseCsaf: true}, []byte(`{}`), func(t *testing.T, err error, r *vmaas.Request) {
			if assert.NoError(t, err) {
				assert.True(t, r.UseCsaf)
			}
		}},
		{
			"use_csaf_true", &vmaas.Request{UseCsaf: true}, []byte(`{"use_csaf": true}`),
			func(t *testing.T, err error, r *vmaas.Request) {
				if assert.NoError(t, err) {
					assert.True(t, r.UseCsaf)
				}
			},
		},
		{
			"use_csaf_false", &vmaas.Request{UseCsaf: true}, []byte(`{"use_csaf": false}`),
			func(t *testing.T, err error, r *vmaas.Request) {
				if assert.NoError(t, err) {
					assert.False(t, r.UseCsaf)
				}
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			testBindJSON(t, test)
		})
	}
}
