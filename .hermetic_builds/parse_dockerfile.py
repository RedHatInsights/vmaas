from pprint import pprint
from dockerfile_parse import DockerfileParser
import re

dfp = DockerfileParser()

with open("Dockerfile", "r") as file:
    dfp.content = file.read()

xxx = dfp.structure
REMOVE = ["-", "--", "RUN" ,"microdnf", "install", "$"]
LIS = []

for l1s in xxx:
    if l1s['instruction'] == 'RUN':
        if 'RUN microdnf' in l1s['content']:
            line = l1s['content']
            commands = re.sub(r'\\\n', ' ', line).split('&&')
            commands = [cmd.strip() for cmd in commands if cmd.strip()]
            for li in commands:
                if 'RUN microdnf' in li:
                    words = li.split()
                    for w in words:
                        if w.startswith(tuple(REMOVE)):
                            pass
                        else:
                            LIS.append(w)


print(LIS)

rpms_in = (
    f'packages: [{', '.join(f"{LIS}" for LIS in LIS)}]\n'
    'contentOrigin:\n'
    '  repofiles: ["./ubi.repo"]\n'
    'arches: [x86_64]'
)

print(rpms_in)

with open("rpms.in.yaml", "w") as wfile:
    wfile.write(rpms_in)
