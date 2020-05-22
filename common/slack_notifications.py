"""
Utilities for sending slack notifications
"""

import os

import requests

SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')
VMAAS_ENV = os.getenv('VMAAS_ENV', 'dev')


def format_message(msg: dict):
    """Msg might be in followed format {header: value, name: cert_name, valid_to: date, expire_in: days}"""
    formatted = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*[{VMAAS_ENV}]* :warning: {msg['header']}! :warning:\n"
                            f":page_with_curl: *Certificate name*: {msg['name']}"
                }
            }

        ]
    }
    date = msg.get('date')

    if date:
        formatted['blocks'].append({"type": "divider"})
        formatted['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":date: *Valid to*: {date['valid_to']:%Y-%m-%d %H:%M}\n"
                        f":hourglass_flowing_sand: *Expire in*: {date['expire_in']} days"
            }
        })

    return formatted


def prepare_msg_for_slack(cert_name, header, expire_tuple=None):
    """Prepare msg_dict for format_message method"""
    msg = {'header': header,
           'name': cert_name if cert_name else 'None'}
    (valid_to_dt, expire_in_days_td) = expire_tuple

    if valid_to_dt and isinstance(expire_in_days_td, int):
        msg['date'] = {'valid_to': valid_to_dt,
                       'expire_in': 0 if expire_in_days_td < 0 else expire_in_days_td}

    return msg


def send_slack_notification(msg: dict):
    """If SLACK_WEBHOOK is set, sends notification to Slack"""
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json=format_message(msg),
                      headers={'Content-type': 'application/json'})
