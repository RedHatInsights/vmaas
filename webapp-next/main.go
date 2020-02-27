package main

import (
	"app/utils"
	"app/webserver"
	"app/websocket"
)

func main() {
	utils.ConfigureLogging()

	msg, err := websocket.TryRefreshCache()
	if err != nil {
		utils.Log("err", err.Error()).Error("Could not refresh cache")
	} else {
		utils.Log("msg", msg).Info("Refreshed cache")
	}
	go websocket.RunWebsocketListener()

	webserver.Run()
}
