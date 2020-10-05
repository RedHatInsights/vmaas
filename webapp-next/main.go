package main

import (
	"app/cache"
	"app/utils"
	"app/webserver"
	"app/websocket"
	"os"
)

func main() {
	utils.ConfigureLogging()

	_, err := os.Stat(websocket.DumpFileName)
	if err != nil {
		cache.LoadCache(websocket.DumpFileName)
	}

	go websocket.RunWebsocketListener()

	webserver.Run()
}
