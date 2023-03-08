package utils

import (
	"fmt"
	"os"
	"strings"
	"time"

	clowder "github.com/redhatinsights/app-common-go/pkg/api/v1"
)

var Cfg = Config{}

type Config struct {
	// database
	DBHost          string
	DBName          string
	DBPort          int
	DBSslMode       string
	DBSslRootCert   string
	DBAdminUser     string
	DBAdminPassword string
	DBUser          string
	DBPassword      string

	// API
	PublicPort  int
	PrivatePort int
	MetricsPort int
	MetricsPath string

	// endpoints
	ReposcanAddress  string
	WebsocketAddress string
	OGWebappAddress  string

	// cloudwatch
	CloudWatchAccessKeyID     string
	CloudWatchSecretAccesskey string
	CloudWatchRegion          string
	CloudWatchLogGroup        string

	// env
	LogLevel             string
	LogStyle             string
	CacheRefreshInterval time.Duration
	EnableProfiler       bool
}

type Endpoint clowder.DependencyEndpoint
type PrivateEndpoint clowder.PrivateDependencyEndpoint

func init() {
	if !clowder.IsClowderEnabled() {
		panic("Missing clowder config")
	}
	initDB()
	initAPI()
	initEndpoints()
	initCloudwatch()
	initEnv()
}

func initDB() {
	Cfg.DBHost = clowder.LoadedConfig.Database.Hostname
	Cfg.DBName = clowder.LoadedConfig.Database.Name
	Cfg.DBPort = clowder.LoadedConfig.Database.Port
	Cfg.DBSslMode = clowder.LoadedConfig.Database.SslMode
	if clowder.LoadedConfig.Database.RdsCa != nil {
		certPath, err := clowder.LoadedConfig.RdsCa()
		if err != nil {
			panic(err)
		}
		Cfg.DBSslRootCert = certPath
	}
	Cfg.DBAdminUser = clowder.LoadedConfig.Database.AdminUsername
	Cfg.DBAdminPassword = clowder.LoadedConfig.Database.AdminPassword
	Cfg.DBUser = clowder.LoadedConfig.Database.Username
	Cfg.DBPassword = clowder.LoadedConfig.Database.Password
}

func initAPI() {
	Cfg.PublicPort = *clowder.LoadedConfig.PublicPort
	Cfg.PrivatePort = *clowder.LoadedConfig.PrivatePort
	Cfg.MetricsPort = clowder.LoadedConfig.MetricsPort
	Cfg.MetricsPath = clowder.LoadedConfig.MetricsPath
}

func initEndpoints() {
	for _, e := range clowder.LoadedConfig.Endpoints {
		if e.App == "vmaas" {
			switch {
			case strings.Contains(e.Name, "reposcan"):
				Cfg.ReposcanAddress = (*Endpoint)(&e).BuildUrl("http")
			case strings.Contains(e.Name, "webapp") && !strings.Contains(e.Name, "go"):
				Cfg.OGWebappAddress = (*Endpoint)(&e).BuildUrl("http")
			}
		}
	}
	for _, e := range clowder.LoadedConfig.PrivateEndpoints {
		if e.App == "vmaas" {
			switch {
			case strings.Contains(e.Name, "websocket"):
				Cfg.WebsocketAddress = fmt.Sprintf("ws://%s:%d", e.Name, e.Port)
			}
		}
	}
}

func initCloudwatch() {
	cwCfg := clowder.LoadedConfig.Logging.Cloudwatch
	if cwCfg != nil {
		Cfg.CloudWatchAccessKeyID = cwCfg.AccessKeyId
		Cfg.CloudWatchSecretAccesskey = cwCfg.SecretAccessKey
		Cfg.CloudWatchRegion = cwCfg.Region
		Cfg.CloudWatchLogGroup = cwCfg.LogGroup
	}
}

func initEnv() {
	Cfg.LogLevel = Getenv("LOG_LEVEL", "INFO")
	Cfg.LogStyle = os.Getenv("LOG_STYLE")
	cacheRefreshSec := GetIntEnvOrDefault("CACHE_REFRESH_INTERVAL", 5*60) // 5 min default
	Cfg.CacheRefreshInterval = time.Second * time.Duration(cacheRefreshSec)
	Cfg.EnableProfiler = GetBoolEnvOrDefault("ENABLE_PROFILER", false)
}

func (e *Endpoint) BuildUrl(scheme string) string {
	return buildUrl(scheme, e.Hostname, e.Port, e.TlsPort)
}

func (e *PrivateEndpoint) BuildUrl(scheme string) string {
	return buildUrl(scheme, e.Hostname, e.Port, e.TlsPort)
}

func buildUrl(scheme, host string, port int, tlsPort *int) string {
	if clowder.LoadedConfig.TlsCAPath != nil {
		scheme += "s"
		if tlsPort != nil {
			port = *tlsPort
		}
	}
	return fmt.Sprintf("%s://%s:%d", scheme, host, port)
}
