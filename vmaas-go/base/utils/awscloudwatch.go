// inspired by:
// https://github.com/RedHatInsights/insights-ingress-go/blob/3ea33a8d793c2154f7cfa12057ca005c5f6031fa/logger/logger.go
//
// https://github.com/kdar/logrus-cloudwatchlogs
package utils

import (
	"os"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	lc "github.com/redhatinsights/platform-go-middlewares/v2/logging/cloudwatch"
	log "github.com/sirupsen/logrus"
)

var hook *lc.LogrusHook

// Try to init CloudWatch logging
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

	cred := credentials.NewStaticCredentials(key, secret, "")
	awsconf := aws.NewConfig().WithRegion(region).WithCredentials(cred)
	writer, err := lc.NewBatchWriterWithDuration(group, hostname, awsconf, 10*time.Second)
	if err != nil {
		LogError("err", err.Error(), "unable to setup CloudWatch logging")
		return
	}
	hook = lc.NewLogrusHook(writer)
	log.AddHook(hook)
	log.Info("CloudWatch logging configured")
}

func FlushLogs() {
	if hook != nil {
		_ = hook.Flush()
	}
}
