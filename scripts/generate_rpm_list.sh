#!/bin/sh

# ./scripts/generate_rpm_list.sh
# Example:
# ./scripts/generate_rpm_list.sh > /tmp/rpm_list.txt
# cat /tmp/rpm_list.txt

rpm -qa --qf='%{sourcerpm}\n' | grep -v '(none)' | sort -u | sed 's/\.src\.rpm$//'
