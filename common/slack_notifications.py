"""
Utilities for sending slack notifications
"""

import os

import requests

SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')
VMAAS_ENV = os.getenv('VMAAS_ENV', 'dev')


def send_slack_notification(message):
    """If SLACK_WEBHOOK is set, sends notification to Slack"""
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json={'text': '[{}] {}'.format(VMAAS_ENV, message)},
                      headers={'Content-type': 'application/json'})
