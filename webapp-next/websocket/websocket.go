package websocket //nolint:golint,stylecheck

import (
	"app/cache"
	"app/utils"
	"fmt"
	"github.com/gorilla/websocket"
	"github.com/pkg/errors"
	"os"
	"time"
)

var Ready = true

type Handler func(data []byte, conn *websocket.Conn) error

func sendMsg(conn *websocket.Conn, msg string) error {
	utils.Log("msg", msg).Info("Sending ws message")
	return conn.WriteMessage(websocket.TextMessage, []byte(msg))
}

func informWebsocket(conn *websocket.Conn) error {
	if cache.C != nil {
		version := fmt.Sprintf("version %s", cache.C.DbChange.Exported.Format(time.RFC3339))
		return errors.Wrap(sendMsg(conn, version), "Sending version")
	}

	msg := "status-ready"
	if !Ready {
		msg = "status-refreshing"
	}

	return errors.Wrap(sendMsg(conn, msg), "Sending status")
}

func TryRefreshCache(conn *websocket.Conn) error {
	Ready = false
	if err := informWebsocket(conn); err != nil {
		return errors.Wrap(err, "Informing about state")
	}

	if err := download(); err != nil {
		return errors.Wrap(err, "downloading dump")
	}
	cache.C = cache.LoadCache(DumpFileName)
	Ready = true
	if err := informWebsocket(conn); err != nil {
		return errors.Wrap(err, "Informing about state")
	}
	return nil
}

func runWebsocket(conn *websocket.Conn, handler Handler) error {
	defer conn.Close()
	var err error
	utils.Log().Info("Starting websocket handler")
	if err = sendMsg(conn, "subscribe-webapp"); err != nil {
		return errors.Wrap(err, "Could not subscribe")
	}

	if err = TryRefreshCache(conn); err != nil {
		return errors.Wrap(err, "Refreshing cache at start")
	}

	for {
		typ, msg, err := conn.ReadMessage()
		if err != nil {
			utils.Log("err", err.Error()).Error("Failed to retrieve VMaaS websocket message")
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

func websocketHandler(data []byte, conn *websocket.Conn) error {
	text := string(data)
	utils.Log("data", string(data)).Info("Received VMaaS websocket message")

	if text == "refresh-cache" {
		err := TryRefreshCache(conn)
		return errors.Wrap(err, "Failed to update cache")
	} else {
		return errors.Errorf("Unknown message %s", text)
	}
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

		err = runWebsocket(conn, websocketHandler)
		if err != nil {
			utils.Log("err", err.Error()).Error("Websocket error occurred, waiting")
		}
		time.Sleep(2 * time.Second)
	}
}
