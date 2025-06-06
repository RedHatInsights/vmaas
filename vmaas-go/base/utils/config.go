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
	if !clowder.IsClowderEnabled() {
		panic("Missing clowder config")
	}
	Cfg.initDB()
	Cfg.initAPI()
	Cfg.initEndpoints()
	Cfg.initCloudwatch()
	Cfg.initEnv()
}

func (c *Config) initDB() {
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
}

func (c *Config) initAPI() {
	c.PublicPort = *clowder.LoadedConfig.PublicPort
	c.PrivatePort = *clowder.LoadedConfig.PrivatePort
	c.MetricsPort = clowder.LoadedConfig.MetricsPort
	c.MetricsPath = clowder.LoadedConfig.MetricsPath
}

func (c *Config) initEndpoints() {
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
			c.DumpAddress = fmt.Sprintf("%s/vmaas.db", (*PrivateEndpoint)(&e).BuildURL("http"))
		}
	}
}

func (c *Config) initCloudwatch() {
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
