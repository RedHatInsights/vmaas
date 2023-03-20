package utils

import (
	"fmt"
	"os"
	"time"

	log "github.com/sirupsen/logrus"
)

// configure logging using env variables
func ConfigureLogging() {
	InitLogging(log.DebugLevel)
	level := parseLogLevel(Cfg.LogLevel)
	log.SetLevel(level)
	if Cfg.LogStyle == "json" {
		initJSONLogStyle()
	}
	trySetupCloudWatchLogging()
}

func processArgs(args []interface{}) (log.Fields, interface{}) {
	nArgs := len(args)
	fields := log.Fields{}
	for i := 1; i < nArgs; i += 2 {
		fields[args[i-1].(string)] = args[i]
	}
	var msg interface{}
	if nArgs%2 != 0 {
		msg = args[nArgs-1]
	} else {
		msg = ""
	}
	return fields, msg
}

// implement LogXXXX functions to enable additional log fields
// usage: utils.LogInfo("my_field_1", 1, "my_field_2", 4.3, "Testing logging")
func logLevel(level log.Level, args ...interface{}) {
	if !log.IsLevelEnabled(level) {
		return
	}
	fields, msg := processArgs(args)

	// using standard Log at Fatal or Panic level will not properly exit or panic
	entry := log.WithFields(fields)
	switch level {
	case log.FatalLevel:
		entry.Fatal(msg)
	case log.PanicLevel:
		entry.Panic(msg)
	default:
		entry.Log(level, msg)
	}
}

func LogTrace(args ...interface{}) {
	logLevel(log.TraceLevel, args...)
}

func LogDebug(args ...interface{}) {
	logLevel(log.DebugLevel, args...)
}

func LogInfo(args ...interface{}) {
	logLevel(log.InfoLevel, args...)
}

func LogWarn(args ...interface{}) {
	logLevel(log.WarnLevel, args...)
}

func LogError(args ...interface{}) {
	logLevel(log.ErrorLevel, args...)
}

func LogFatal(args ...interface{}) {
	logLevel(log.FatalLevel, args...)
}

func LogPanic(args ...interface{}) {
	logLevel(log.PanicLevel, args...)
}

// parse log.Level from string or fail
func parseLogLevel(strlevel string) log.Level {
	level, err := log.ParseLevel(strlevel)
	if err != nil {
		panic(fmt.Errorf("unable to parse log level: %v", err))
	}
	return level
}

// configure logging to stdout with given loglevel
func InitLogging(level log.Level) {
	log.SetOutput(os.Stdout)
	log.SetLevel(level)
}

// configure json logging format for Logstash
func initJSONLogStyle() {
	log.SetFormatter(&log.JSONFormatter{
		TimestampFormat: time.RFC3339,
		FieldMap: log.FieldMap{
			log.FieldKeyTime:  "@timestamp",
			log.FieldKeyLevel: "levelname",
			log.FieldKeyMsg:   "message",
		},
	})
}

// LogProgress Show progress of the operation
func LogProgress(msg string, duration time.Duration, total int64) (*time.Ticker, *int64) {
	var count int64
	timer := time.NewTicker(duration)
	goID := GetGorutineID()

	go func() {
		for range timer.C {
			pct := count * 100 / total
			LogInfo("gorutineID", goID, "progress %", pct, msg)
		}
	}()
	return timer, &count
}
