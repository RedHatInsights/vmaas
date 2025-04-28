package core

import (
	"fmt"

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
	utils.ConfigureConfig()
	utils.ConfigureLogging()
}

func ConfigureCache() {
	var err error
	VmaasAPI, err = vmaas.InitFromURL(
		utils.Cfg.DumpAddress,
		vmaas.WithMaxGoroutines(utils.Cfg.VmaasLibMaxGoroutines),
		vmaas.WithUnfixed(utils.Cfg.UnfixedEvalEnabled),
		vmaas.WithNewerReleaseverRepos(utils.Cfg.NewerReleaseverRepos),
		vmaas.WithNewerReleaseverCsaf(utils.Cfg.NewerReleaseverCsaf),
		vmaas.WithVmaasVersionFilePath(utils.Cfg.VmaasVersionFilePath),
	)
	if err != nil {
		utils.LogWarn("err", err.Error(), "Cache not available on app start")
	}
	VmaasAPI.PeriodicCacheReload(
		utils.Cfg.CacheRefreshInterval,
		fmt.Sprintf("%s/api/v1/latestdump", utils.Cfg.ReposcanAddress),
		nil, // not needed, cache initialized from url
	)
}

func SetupTestEnvironment() {
	utils.SetDefaultEnvOrFail("LOG_LEVEL", "debug")
	ConfigureApp()
}

func SetupTest() {
	if !testSetupRan {
		SetupTestEnvironment()
		testSetupRan = true
	}
}
