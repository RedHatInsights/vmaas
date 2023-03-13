package core

import (
	"fmt"
	"testing"

	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/utils"
)

var (
	DefaultLimit  = 20
	DefaultOffset = 0
	testSetupRan  = false
	VmaasAPI      *vmaas.API
)

func ConfigureApp() {
	utils.ConfigureLogging()
}

func ConfigureCache() {
	var err error
	VmaasAPI, err = vmaas.InitFromURL(fmt.Sprintf("%s/api/v1/latestdumpdownload", utils.Cfg.ReposcanAddress))
	if err != nil {
		utils.Log("err", err.Error()).Warn("Cache not available on app start")
	}
	VmaasAPI.PeriodicCacheReload(
		utils.Cfg.CacheRefreshInterval,
		fmt.Sprintf("%s/api/v1/latestdump", utils.Cfg.ReposcanAddress),
		nil, // not needed, cache initialized from API url
	)
}

func SetupTestEnvironment() {
	utils.SetDefaultEnvOrFail("LOG_LEVEL", "debug")
	ConfigureApp()
}

func SetupTest(t *testing.T) {
	if !testSetupRan {
		SetupTestEnvironment()
		testSetupRan = true
	}
}
