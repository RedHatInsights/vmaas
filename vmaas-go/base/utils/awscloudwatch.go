// inspired by:
// https://github.com/RedHatInsights/insights-ingress-go/blob/3ea33a8d793c2154f7cfa12057ca005c5f6031fa/logger/logger.go
//
// https://github.com/kdar/logrus-cloudwatchlogs
// https://github.com/lzap/cloudwatchwriter2
package utils

import (
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatchlogs"
	cww "github.com/lzap/cloudwatchwriter2"
	log "github.com/sirupsen/logrus"
)

type CloudWatchHook struct {
	writer *cww.CloudWatchWriter
}

func (h *CloudWatchHook) Fire(entry *log.Entry) error {
	line, err := entry.String()
	if err != nil {
		return err
	}
	_, err = h.writer.Write([]byte(line))
	return err
}

func (h *CloudWatchHook) Levels() []log.Level {
	return log.AllLevels
}

func (h *CloudWatchHook) Flush() error {
	return h.writer.Close()
}

var hook *CloudWatchHook

func trySetupCloudWatchLogging() {
	key := Cfg.CloudWatchAccessKeyID
	if key == "" {
		log.Info("config for aws CloudWatch not loaded")
		return
	}

	secret := FailIfEmpty(Cfg.CloudWatchSecretAccesskey, "CW_AWS_SECRET_ACCESS_KEY")
	region := Cfg.CloudWatchRegion
	group := Cfg.CloudWatchLogGroup

	hostname, err := os.Hostname()
	if err != nil {
		LogError("err", err.Error(), "unable to get hostname to set CloudWatch log_stream")
		return
	}

	log.SetFormatter(&log.JSONFormatter{
		TimestampFormat: "2006-01-02T15:04:05.999Z",
		FieldMap: log.FieldMap{
			log.FieldKeyTime:  "@timestamp",
			log.FieldKeyLevel: "level",
			log.FieldKeyMsg:   "message",
		},
	})

	options := cloudwatchlogs.Options{
		Region:      region,
		Credentials: credentials.NewStaticCredentialsProvider(key, secret, ""),
	}
	client := cloudwatchlogs.New(options)

	writer, err := cww.NewWithClient(client, 10*time.Second, group, hostname)
	if err != nil {
		LogError("err", err.Error(), "unable to setup CloudWatch logging")
		return
	}

	hook = &CloudWatchHook{writer: writer}
	log.AddHook(hook)
	log.Info("CloudWatch logging configured")
}

func FlushLogs() {
	if hook != nil {
		_ = hook.Flush()
	}
}
