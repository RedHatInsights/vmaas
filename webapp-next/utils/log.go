package utils

import (
	"fmt"
	"os"
	"time"

	log "github.com/sirupsen/logrus"
)

// configure logging using env variables
func ConfigureLogging() {
	InitLogging(log.TraceLevel)
	strlevel := os.Getenv("LOG_LEVEL")
	if strlevel == "" {
		strlevel = "TRACE"
	}
	level := parseLogLevel(strlevel)
	log.SetLevel(level)
	style := os.Getenv("LOG_STYLE")
	if style == "json" {
		initJSONLogStyle()
	}
}

// implement Log function to enable additional log fields
// usage: utils.Log("my_field_1", 1, "my_field_2", 4.3).Info("Testing logging")
func Log(args ...interface{}) *log.Entry {
	nArgs := len(args)
	fields := log.Fields{}
	if nArgs%2 != 0 {
		log.Warningf("Unable to accept odd (%d) arguments count in utils.DebugLog method.", nArgs)
	} else {
		for i := 0; i < nArgs; i += 2 {
			fields[args[i].(string)] = args[i+1]
		}
	}
	return log.WithFields(fields)
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
