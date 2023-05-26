package base

import (
	"context"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/redhatinsights/vmaas/base/utils"

	"github.com/gin-gonic/gin"
)

var (
	Context       context.Context
	CancelContext context.CancelFunc
)

func init() {
	Context, CancelContext = context.WithCancel(context.Background())
}

func HandleSignals() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-c
		CancelContext()
		utils.LogInfo("SIGTERM/SIGINT handled")
	}()
}

func remove(r rune) rune {
	if r == 0 {
		return -1
	}
	return r
}

// Removes characters, which are not accepted by postgresql driver
// in parameter values
func RemoveInvalidChars(s string) string {
	return strings.Map(remove, s)
}

// TryExposeOnMetricsPort Expose app on required port if set
func TryExposeOnMetricsPort(app *gin.Engine) {
	metricsPort := utils.Cfg.MetricsPort
	if metricsPort == -1 {
		return // Do not expose extra metrics port if not set
	}
	err := utils.RunServer(Context, app, metricsPort)
	if err != nil {
		utils.LogError("err", err.Error())
		panic(err)
	}
}
