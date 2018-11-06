current_user=$(oc whoami 2> /dev/null)

if [ "$current_user" == "" ]; then
    echo "Please login to OpenShift cluster and select project."
    exit 1
fi

filter="$2"
if [ "$filter" != "" ]; then
    dcs=$(oc get dc 2> /dev/null | tail -n +2 | awk '{print $1}' | grep "$filter")
else
    dcs=$(oc get dc 2> /dev/null | tail -n +2 | awk '{print $1}')
fi

echo "$(oc project)"
echo "Logged in as user \"$current_user\"."
echo ""
if [ "$dcs" == "" ]; then
    echo "No deployment configs found in project. Exiting."
    exit 2
fi

warning="$warning"
echo "$warning"

for dc in $dcs; do
    echo "$dc"
done
echo ""
echo -n "Continue? [y/N] "

read choice
choice=$(echo $choice | awk '{print toupper($0)}')

if [ "$choice" != "Y" ]; then
    echo "Exiting."
    exit 3
fi

action="$3"

for dc in $dcs; do
    containers=$(oc get dc/$dc -o json | python -c "import sys,json;obj=json.load(sys.stdin);containers=obj['spec']['template']['spec']['containers'];print(' '.join([c['name'] for c in containers]))" | wc -w)
    containers=$((containers-1))
    for i in $(seq 0 $containers); do
	if [ "$action" == "remove-resources" ]; then
            oc patch dc/$dc --type json -p "[{\"op\": \"remove\", \"path\": \"/spec/template/spec/containers/$i/resources\"}]"
	elif [ "$action" == "devel-container" ]; then
	    oc patch dc/$dc --type json -p "[{\"op\": \"add\", \"path\": \"/spec/template/spec/containers/$i/command\", \"value\": [\"sleep\", \"infinity\"]}]"
	    oc patch dc/$dc --type json -p "[{\"op\": \"add\", \"path\": \"/spec/template/spec/containers/$i/securityContext\", \"value\": {\"runAsUser\": '0'}}]"
	fi
    done
done

echo ""
echo "Done."
