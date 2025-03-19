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
	EnableGoCves         bool
	EnableGoErrata       bool
	EnableGoRepos        bool
	EnableGoPackages     bool
	EnableGoPkgList      bool
	EnableGoPkgTree      bool
	EnableGoPatches      bool
	EnableGoRPMPkgNames  bool
	EnableGoSRPMPkgNames bool
	EnableGoDBChange     bool
	EnableGoVersion      bool

	// lib
	UnfixedEvalEnabled    bool
	VmaasLibMaxGoroutines int
	NewerReleaseverRepos  bool
	NewerReleaseverCsaf   bool
}

type (
	Endpoint        clowder.DependencyEndpoint
	PrivateEndpoint clowder.PrivateDependencyEndpoint
)

func ConfigureConfig() {
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
				Cfg.ReposcanAddress = (*Endpoint)(&e).BuildURL("http")
			case strings.Contains(e.Name, "webapp") && !strings.Contains(e.Name, "go"):
				Cfg.OGWebappAddress = (*Endpoint)(&e).BuildURL("http")
			}
		}
	}
	for _, e := range clowder.LoadedConfig.PrivateEndpoints {
		if e.App == "vmaas" && strings.Contains(e.Name, "reposcan") {
			Cfg.DumpAddress = fmt.Sprintf("%s/vmaas.db", (*PrivateEndpoint)(&e).BuildURL("http"))
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
	cacheRefreshSec := GetIntEnvOrDefault("CACHE_REFRESH_INTERVAL", 60) // 1 min default
	Cfg.CacheRefreshInterval = time.Second * time.Duration(cacheRefreshSec)
	Cfg.EnableProfiler = GetBoolEnvOrDefault("ENABLE_PROFILER", false)
	Cfg.UnfixedEvalEnabled = GetBoolEnvOrDefault("CSAF_UNFIXED_EVAL_ENABLED", true)
	Cfg.VmaasLibMaxGoroutines = GetIntEnvOrDefault("VMAAS_LIB_MAX_GOROUTINES", 20)
	Cfg.NewerReleaseverRepos = GetBoolEnvOrDefault("NEWER_RELEASEVER_REPOS", true)
	Cfg.NewerReleaseverCsaf = GetBoolEnvOrDefault("NEWER_RELEASEVER_CSAF", true)
	Cfg.EnableGoCves = GetBoolEnvOrDefault("ENABLE_GO_CVES", false)
	Cfg.EnableGoErrata = GetBoolEnvOrDefault("ENABLE_GO_ERRATA", false)
	Cfg.EnableGoRepos = GetBoolEnvOrDefault("ENABLE_GO_REPOS", false)
	Cfg.EnableGoPackages = GetBoolEnvOrDefault("ENABLE_GO_PACKAGES", false)
	Cfg.EnableGoPkgList = GetBoolEnvOrDefault("ENABLE_GO_PKGLIST", false)
	Cfg.EnableGoPkgTree = GetBoolEnvOrDefault("ENABLE_GO_PKGTREE", false)
	Cfg.EnableGoPatches = GetBoolEnvOrDefault("ENABLE_GO_PATCHES", false)
	Cfg.EnableGoRPMPkgNames = GetBoolEnvOrDefault("ENABLE_GO_RPMPKGNAMES", false)
	Cfg.EnableGoSRPMPkgNames = GetBoolEnvOrDefault("ENABLE_GO_SRPMPKGNAMES", false)
	Cfg.EnableGoDBChange = GetBoolEnvOrDefault("ENABLE_GO_DBCHANGE", false)
	Cfg.EnableGoVersion = GetBoolEnvOrDefault("ENABLE_GO_VERSION", false)
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
