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
		switch os.Args[1] {
		case "webapp":
			webapp.Run()
			return
		}
	}
	log.Panic("You need to provide a command")
}
