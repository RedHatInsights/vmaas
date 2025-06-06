package utils

import (
	"testing"

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
