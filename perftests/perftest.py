#!/bin/env python3

import os
import sys
import time
import requests
import subprocess
import argparse

SUITE_NAME = "unknown"

REPOSCAN_HOST = 'http://localhost:8081'
WEBAPP_HOST = 'http://localhost:8080'

PKG_COUNT = 1500

AUTH_HEADERS = {"Authorization": "token token"}
BENCH_ENV = os.environ.copy()


def wait_for_finished():
    while True:
        status = requests.get(f"{REPOSCAN_HOST}/api/v1/task/status", headers=AUTH_HEADERS).json()
        time.sleep(5)
        if not status['running']:
            print('Last task finished')
            break


def import_repolist():
    resp = requests.post(f"{REPOSCAN_HOST}/api/v1/repos", open('./repolist.json').read(),
                         headers={"Content-Type": "application/json", **AUTH_HEADERS}).json()
    print(f"Started load : {resp}")
    assert resp['success'] == True
    wait_for_finished()


def perform_sync():
    resp = requests.put(f"{REPOSCAN_HOST}/api/v1/sync", headers=AUTH_HEADERS).json()
    print(f"Started sync : {resp}")
    assert resp['success'] == True
    wait_for_finished()


def bench(out_file: str, name: str, threads: int, conns: int, rate: int, pkgs: int, secs: int = 60):
    env = {"OUT_FILE": f"{out_file}", "TEST_NAME": f"{name}", "PKG_COUNT": f"{pkgs}", **BENCH_ENV}
    cmd = ["./wrk", f"-t{threads}", f"-c{conns}", "-R", f"{rate}", f"-d{secs}s", "--timeout", "10s", f"{WEBAPP_HOST}",
           "-s", "./script.lua"]
    subprocess.run(cmd, env=env)


def sync_cmd(args):
    global REPOSCAN_HOST
    REPOSCAN_HOST = args.reposcan
    import_repolist()
    perform_sync()
    pass


def bench_cmd(args):
    global SUITE_NAME, WEBAPP_HOST, PKG_COUNT
    SUITE_NAME = args.suite_name
    WEBAPP_HOST = args.webapp
    PKG_COUNT = args.pkg_count

    os.makedirs('out', exist_ok=True)

    for pkg_count in [500, 1500]:
        for reqs in [1, 5, 10, 50, 100]:
            print("---------- %s pkgs, %s Req/s test ----------" % (pkg_count, reqs))
            bench(SUITE_NAME, '%s pkgs @ %s req/s' % (pkg_count, reqs), 1, max(1, reqs // 10), reqs, pkg_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command')

    bench_parser = subparsers.add_parser('bench', help='Benchmark')
    bench_parser.add_argument('--webapp', '-w', type=str, default=WEBAPP_HOST, help="Webapp host")
    bench_parser.add_argument('--suite-name', '-n', type=str, default=SUITE_NAME)
    bench_parser.add_argument('--pkg-count', '-p', type=int, default=PKG_COUNT)
    bench_parser.set_defaults(func=bench_cmd)

    sync_parser = subparsers.add_parser('sync', help='Synchronize database')
    sync_parser.add_argument('--reposcan', '-r', type=str, default=REPOSCAN_HOST, help="Reposcan host")
    sync_parser.set_defaults(func=sync_cmd)

    args = parser.parse_args(sys.argv[1:])

    if hasattr(args, 'func'):
        args.func(args)
    else:
        raise ValueError("Did not provide a valid subcommand")
