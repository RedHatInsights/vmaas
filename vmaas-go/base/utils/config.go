package utils

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	clowder "github.com/redhatinsights/app-common-go/pkg/api/v1"
)

const DumpPath = "/vmaas.db"

var Cfg = Config{}

type Config struct {
	// Clowder
	isClowder bool

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
	ReposcanAddress string
	DumpAddress     string
	OGWebappAddress string

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

	// lib
	UnfixedEvalEnabled    bool
	VmaasLibMaxGoroutines int
	NewerReleaseverRepos  bool
	NewerReleaseverCsaf   bool
	VmaasVersionFilePath  string
}

type (
	Endpoint        clowder.DependencyEndpoint
	PrivateEndpoint clowder.PrivateDependencyEndpoint
)

func ConfigureConfig() {
	Cfg.isClowder = clowder.IsClowderEnabled()
	Cfg.initDB()
	Cfg.initAPI()
	Cfg.initEndpoints()
	Cfg.initCloudwatch()
	Cfg.initEnv()
}

func (c *Config) initDB() {
	if c.isClowder {
		c.DBHost = clowder.LoadedConfig.Database.Hostname
		c.DBName = clowder.LoadedConfig.Database.Name
		c.DBPort = clowder.LoadedConfig.Database.Port
		c.DBSslMode = clowder.LoadedConfig.Database.SslMode
		if clowder.LoadedConfig.Database.RdsCa != nil {
			certPath, err := clowder.LoadedConfig.RdsCa()
			if err != nil {
				panic(err)
			}
			c.DBSslRootCert = certPath
		}
		c.DBAdminUser = clowder.LoadedConfig.Database.AdminUsername
		c.DBAdminPassword = clowder.LoadedConfig.Database.AdminPassword
		c.DBUser = clowder.LoadedConfig.Database.Username
		c.DBPassword = clowder.LoadedConfig.Database.Password
	} else {
		var err error
		c.DBHost = os.Getenv("POSTGRESQL_HOST")
		c.DBName = os.Getenv("POSTGRESQL_DB")
		c.DBPort, err = strconv.Atoi(Getenv("POSTGRESQL_PORT", "5432"))
		if err != nil {
			LogPanic("err", err, "POSTGRESQL_PORT environment variable is not an integer")
		}
		c.DBSslMode = Getenv("POSTGRESQL_SSL_MODE", "prefer")
		c.DBSslRootCert = os.Getenv("POSTGRESQL_SSL_ROOT_CERT_PATH")
		c.DBUser = os.Getenv("POSTGRESQL_USER")
		c.DBPassword = os.Getenv("POSTGRESQL_PASSWORD")
	}
}

func (c *Config) initAPI() {
	if c.isClowder {
		c.PublicPort = *clowder.LoadedConfig.PublicPort
		c.PrivatePort = *clowder.LoadedConfig.PrivatePort
		c.MetricsPort = clowder.LoadedConfig.MetricsPort
		c.MetricsPath = clowder.LoadedConfig.MetricsPath
	} else {
		var err error
		c.PublicPort, err = strconv.Atoi(Getenv("BIND_PUBLIC_PORT", "8000"))
		if err != nil {
			LogPanic("err", err, "BIND_PUBLIC_PORT environment variable is not an integer")
		}

		c.PrivatePort, err = strconv.Atoi(Getenv("BIND_PRIVATE_PORT", "10000"))
		if err != nil {
			LogPanic("err", err, "BIND_PRIVATE_PORT environment variable is not an integer")
		}

		c.MetricsPort, err = strconv.Atoi(Getenv("PROMETHEUS_PORT", "9000"))
		if err != nil {
			LogPanic("err", err, "PROMETHEUS_PORT environment variable is not an integer")
		}
		c.MetricsPath = "/metrics"
	}
}

func (c *Config) initEndpoints() {
	if c.isClowder {
		for _, e := range clowder.LoadedConfig.Endpoints {
			if e.App == "vmaas" {
				switch {
				case strings.Contains(e.Name, "reposcan"):
					c.ReposcanAddress = (*Endpoint)(&e).BuildURL("http")
				case strings.Contains(e.Name, "webapp") && !strings.Contains(e.Name, "go"):
					c.OGWebappAddress = (*Endpoint)(&e).BuildURL("http")
				}
			}
		}
		for _, e := range clowder.LoadedConfig.PrivateEndpoints {
			if e.App == "vmaas" && strings.Contains(e.Name, "reposcan") {
				c.DumpAddress = fmt.Sprintf("%s%s", (*PrivateEndpoint)(&e).BuildURL("http"), DumpPath)
			}
		}
	} else {
		c.ReposcanAddress = os.Getenv("REPOSCAN_PUBLIC_URL")
		if reposcanPrivateURL := os.Getenv("REPOSCAN_PRIVATE_URL"); reposcanPrivateURL != "" {
			c.DumpAddress = fmt.Sprintf("%s%s", reposcanPrivateURL, DumpPath)
		}

		c.OGWebappAddress = os.Getenv("WEBAPP_URL")
	}
}

func (c *Config) initCloudwatch() {
	if !c.isClowder {
		return
	}

	cwCfg := clowder.LoadedConfig.Logging.Cloudwatch
	if cwCfg != nil {
		c.CloudWatchAccessKeyID = cwCfg.AccessKeyId
		c.CloudWatchSecretAccesskey = cwCfg.SecretAccessKey
		c.CloudWatchRegion = cwCfg.Region
		c.CloudWatchLogGroup = cwCfg.LogGroup
	}
}

func (c *Config) initEnv() {
	c.LogLevel = Getenv("LOG_LEVEL", "INFO")
	c.LogStyle = os.Getenv("LOG_STYLE")
	cacheRefreshSec := GetIntEnvOrDefault("CACHE_REFRESH_INTERVAL", 60) // 1 min default
	c.CacheRefreshInterval = time.Second * time.Duration(cacheRefreshSec)
	c.EnableProfiler = GetBoolEnvOrDefault("ENABLE_PROFILER", false)
	c.UnfixedEvalEnabled = GetBoolEnvOrDefault("CSAF_UNFIXED_EVAL_ENABLED", true)
	c.VmaasLibMaxGoroutines = GetIntEnvOrDefault("VMAAS_LIB_MAX_GOROUTINES", 20)
	c.NewerReleaseverRepos = GetBoolEnvOrDefault("NEWER_RELEASEVER_REPOS", true)
	c.NewerReleaseverCsaf = GetBoolEnvOrDefault("NEWER_RELEASEVER_CSAF", true)
	c.VmaasVersionFilePath = Getenv("VMAAS_VERSION_FILE_PATH", "/vmaas/VERSION")
}

func (e *Endpoint) BuildURL(scheme string) string {
	return buildURL(scheme, e.Hostname, e.Port, e.TlsPort)
}

func (e *PrivateEndpoint) BuildURL(scheme string) string {
	return buildURL(scheme, e.Hostname, e.Port, e.TlsPort)
}

func buildURL(scheme, host string, port int, tlsPort *int) string {
	if clowder.LoadedConfig.TlsCAPath != nil {
		scheme += "s"
		if tlsPort != nil {
			port = *tlsPort
		}
	}
	return fmt.Sprintf("%s://%s:%d", scheme, host, port)
}
