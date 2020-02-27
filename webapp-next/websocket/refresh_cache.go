package websocket

import (
	"app/cache"
	"app/utils"
	"os/exec"
)

var DumpFileName = "/data/vmaas.db"
var RemoteDumpName = "rsync://" + utils.MustGetEnv("REPOSCAN_HOST") + ":8730/data/vmaas.db"

func download() error {
	utils.Log().Trace("Downloading dump from reposcan")
	cmd := exec.Command("rsync", "-a", "--copy-links", "--quiet", RemoteDumpName, DumpFileName)
	utils.Log("cmd", cmd).Info("Running download command")
	out, err := cmd.CombinedOutput()
	if err != nil {
		utils.Log("stdout", string(out), "err", err.Error()).Error("Failed to rsync dump")
		return err
	}
	return nil
}

func TryRefreshCache() (string, error) {
	err := download()
	if err != nil {
		return "", err
	}
	cache.C = cache.LoadCache(DumpFileName)
	return "refreshed " + cache.C.DbChange[0].Exported.String(), nil
}
