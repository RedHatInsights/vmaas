package utils

import (
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

func ObserveSecondsSince(timeStart time.Time, observer prometheus.Observer) {
	observer.Observe(time.Since(timeStart).Seconds())
}

func ObserveHoursSince(timeStart time.Time, observer prometheus.Observer) {
	observer.Observe(time.Since(timeStart).Hours())
}
