package utils

import (
	"log"
	"time"
)

func TimeTrack(start time.Time, eventName string) {
    elapsed := time.Since(start)
    log.Printf("'%s' info loaded (%.3f s)", eventName, elapsed.Seconds())
}
