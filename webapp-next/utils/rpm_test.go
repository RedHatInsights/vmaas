package utils

import (
	"github.com/stretchr/testify/assert"
	"testing"
)

func TestParseNevra(t *testing.T) {
	res, err := ParseNevra("tcpdump-14:4.9.2-4.el7.x86_64")
	assert.NoError(t, err)
	assert.Equal(t, "tcpdump", res.Name)
	assert.Equal(t, 14, res.Epoch)
}
