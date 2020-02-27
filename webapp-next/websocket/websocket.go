package websocket //nolint:golint,stylecheck

import (
	"app/utils"
	"github.com/gorilla/websocket"
	"os"
	"time"
)

type Handler func(data []byte, conn *websocket.Conn) error

func runWebsocket(conn *websocket.Conn, handler Handler) error {
	defer conn.Close()

	err := conn.WriteMessage(websocket.TextMessage, []byte("subscribe-webapp"))
	if err != nil {
		utils.Log("err", err.Error()).Fatal("Could not subscribe for updates")
		return err
	}

	for {
		typ, msg, err := conn.ReadMessage()
		if err != nil {
			utils.Log("err", err.Error()).Fatal("Failed to retrieve VMaaS websocket message")
			return err
		}
		utils.Log("messageType", typ).Info("websocket message received")

		if typ == websocket.BinaryMessage || typ == websocket.TextMessage {
			err = handler(msg, conn)
			if err != nil {
				return err
			}
			continue
		}

		if typ == websocket.PingMessage {
			err = conn.WriteMessage(websocket.PongMessage, msg)
			if err != nil {
				return err
			}
			continue
		}

		if typ == websocket.CloseMessage {
			return nil
		}
	}
}

func loadDumpHandler(data []byte, conn *websocket.Conn) error {
	text := string(data)
	utils.Log("data", string(data)).Info("Received VMaaS websocket message")

	if text == "refresh-cache" {
		msg, err := TryRefreshCache()
		if err != nil {
			utils.Log("err", err.Error()).Fatal("Failed to refresh cache")
		} else {
			err = conn.WriteMessage(websocket.TextMessage, []byte(msg))
			if err != nil {
				utils.Log("err", err.Error()).Fatal("Failed to notify websocket about cache update")
				return err
			}
		}
	}
	return nil
}

func RunWebsocketListener() {
	utils.Log().Info("Listening for websocket database dump updates")
	// Continually try to reconnect
	for {
		addr := "ws://" + os.Getenv("WEBSOCKET_HOST") + ":8082"
		conn, _, err := websocket.DefaultDialer.Dial(addr, nil)
		if err != nil {
			utils.Log("err", err.Error()).Fatal("Failed to connect to VMaaS")
		}

		err = runWebsocket(conn, loadDumpHandler)
		if err != nil {
			utils.Log("err", err.Error()).Error("Websocket error occurred, waiting")
		}
		time.Sleep(2 * time.Second)
	}
}
