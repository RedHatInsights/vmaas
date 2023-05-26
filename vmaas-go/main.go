package main

import (
	"log"
	"os"

	"github.com/redhatinsights/vmaas/base"
	"github.com/redhatinsights/vmaas/base/utils"
	"github.com/redhatinsights/vmaas/webapp"
)

func main() {
	base.HandleSignals()

	defer utils.LogPanics(true)
	if len(os.Args) > 1 {
		if os.Args[1] == "webapp" {
			webapp.Run()
			return
		}
	}
	log.Panic("You need to provide a command")
}
