package utils

import (
	"os"
	"testing"
	"time"

	clowder "github.com/redhatinsights/app-common-go/pkg/api/v1"
	"github.com/stretchr/testify/assert"
)

// Smoke test for default values when clowder is turned off.
// Changing the default values might cause a braking change.
func TestSmokeEnvDefault(t *testing.T) {
	cfg := Config{}
	cfg.initDB()
	cfg.initAPI()
	cfg.initEndpoints()
	cfg.initCloudwatch()
	cfg.initEnv()

	assert.Equal(t, 5432, cfg.DBPort)
	assert.Equal(t, "prefer", cfg.DBSslMode)

	assert.Equal(t, 8000, cfg.PublicPort)
	assert.Equal(t, 9000, cfg.MetricsPort)
	assert.Equal(t, 10000, cfg.PrivatePort)
	assert.Equal(t, "/metrics", cfg.MetricsPath)

	assert.Equal(t, "INFO", cfg.LogLevel)
	assert.Equal(t, false, cfg.EnableProfiler)
	assert.Equal(t, true, cfg.UnfixedEvalEnabled)
	assert.Equal(t, true, cfg.NewerReleaseverRepos)
	assert.Equal(t, true, cfg.NewerReleaseverCsaf)
	assert.Equal(t, "/vmaas/VERSION", cfg.VmaasVersionFilePath)
}

// TestBuildURL tests the buildURL function with different TLS configurations
func TestBuildURL(t *testing.T) {
	if clowder.LoadedConfig == nil {
		clowder.LoadedConfig = &clowder.AppConfig{}
	}

	tests := []struct {
		name    string
		scheme  string
		host    string
		port    int
		tlsPort *int
		hasTLS  bool
		want    string
	}{
		{
			name:    "HTTP without TLS",
			scheme:  "http",
			host:    "localhost",
			port:    8000,
			tlsPort: nil,
			hasTLS:  false,
			want:    "http://localhost:8000",
		},
		{
			name:    "HTTP upgrades to HTTPS when TLS enabled with custom TLS port",
			scheme:  "http",
			host:    "api.example.com",
			port:    8000,
			tlsPort: intPtr(8443),
			hasTLS:  true,
			want:    "https://api.example.com:8443",
		},
		{
			name:    "HTTP upgrades to HTTPS when TLS enabled without custom TLS port",
			scheme:  "http",
			host:    "api.example.com",
			port:    8000,
			tlsPort: nil,
			hasTLS:  true,
			want:    "https://api.example.com:8000",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.hasTLS {
				clowder.LoadedConfig.TlsCAPath = strPtr("/path/to/ca.crt")
			} else {
				clowder.LoadedConfig.TlsCAPath = nil
			}

			result := buildURL(tt.scheme, tt.host, tt.port, tt.tlsPort)
			assert.Equal(t, tt.want, result, "buildURL should return correct URL format")
		})
	}
}

// TestCustomEnvVars verifies that config actually reads from environment variables
// and doesn't just use hardcoded defaults.
func TestCustomEnvVars(t *testing.T) {
	originalPort := os.Getenv("POSTGRESQL_PORT")
	originalLogLevel := os.Getenv("LOG_LEVEL")
	originalCacheRefresh := os.Getenv("CACHE_REFRESH_INTERVAL")

	defer func() {
		if originalPort == "" {
			os.Unsetenv("POSTGRESQL_PORT")
		} else {
			os.Setenv("POSTGRESQL_PORT", originalPort)
		}
		if originalLogLevel == "" {
			os.Unsetenv("LOG_LEVEL")
		} else {
			os.Setenv("LOG_LEVEL", originalLogLevel)
		}
		if originalCacheRefresh == "" {
			os.Unsetenv("CACHE_REFRESH_INTERVAL")
		} else {
			os.Setenv("CACHE_REFRESH_INTERVAL", originalCacheRefresh)
		}
	}()

	os.Setenv("POSTGRESQL_PORT", "6543")
	os.Setenv("LOG_LEVEL", "DEBUG")
	os.Setenv("CACHE_REFRESH_INTERVAL", "120")

	cfg := Config{}
	cfg.initDB()
	cfg.initEnv()

	assert.Equal(t, 6543, cfg.DBPort)
	assert.Equal(t, "DEBUG", cfg.LogLevel)
	assert.Equal(t, 120*time.Second, cfg.CacheRefreshInterval)
}

func intPtr(i int) *int { return &i }

func strPtr(s string) *string { return &s }
