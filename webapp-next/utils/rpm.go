package utils

import (
	"fmt"
	"github.com/pkg/errors"
	"regexp"
	"strconv"
	"strings"
)

var (
	nevraRegex *regexp.Regexp
)

func init() {
	nevraRegex = regexp.MustCompile(
		`((?P<e1>[0-9]+):)?(?P<pn>[^:]+)-((?P<e2>[0-9]+):)?(?P<ver>[^-:]+)-(?P<rel>[^-:]+)\.(?P<arch>[a-z0-9_]+)`)
}

type Nevra struct {
	Name    string
	Epoch   int
	Version string
	Release string
	Arch    string
}

func (n Nevra) String() string {
	var epoch string
	if n.Epoch != 0 {
		epoch = fmt.Sprintf("%v:", n.Epoch)
	}
	return fmt.Sprintf("%s-%s%s-%s.%s", n.Name, epoch, n.Version, n.Release, n.Arch)
}

// parse package components
func ParseNevra(nevra string) (Nevra, error) {
	nevra = strings.TrimSuffix(nevra, ".rpm")
	parsed := nevraRegex.FindStringSubmatch(nevra)
	if len(parsed) != 9 {
		return Nevra{}, errors.New("unable to parse nevra")
	}
	var epoch int
	var err error
	if parsed[5] != "" {
		epoch, err = strconv.Atoi(parsed[5])
		if err != nil {
			return Nevra{}, err
		}
	}
	res := Nevra{
		Name:    parsed[3],
		Epoch:   epoch,
		Version: parsed[6],
		Release: parsed[7],
		Arch:    parsed[8],
	}
	return res, nil
}

func FormatNevra(name string, epoch int, version, release, arch string) string {
	if epoch > 0 {
		return fmt.Sprintf("%s-%d:%s-%s.%s", name, epoch, version, release, arch)
	}
	return fmt.Sprintf("%s-%s-%s.%s", name, version, release, arch)
}
