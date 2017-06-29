#!/usr/bin/env python3
# coding=utf-8
import logging
import hmac

from flask import Flask, request, abort
from requests import post
from markdown import markdown

import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config.FlaskConfig)


def validate_signature():
    logger.debug("Validating request digest")

    mode, digest = request.headers["X-Hub-Signature"].split('=')
    real_hmac = hmac.new(config.WEBHOOK_SECRET, request.data, mode)
    if not hmac.compare_digest(digest, real_hmac.hexdigest()):
        raise ValueError("Invalid HMAC")


def release_published(release, repo):
    logger.debug("New release: %s", release["tag_name"])

    project_name = config.PRETTY_NAMES.get(repo["name"], repo["name"])

    title = release["tag_name"]
    if not release["body"]:
        logger.warning("Empty release notes")
        notes = "No release notes."

    if config.CONFLUENCE_API:
        Update_confluence.delay(title, notes, project_name)


def Update_confluence(title, notes, project_name):
    logger.info("Creating confluence relase notes for: %s", title)

    auth = (config.CONFLUENCE_USER, config.CONFLUENCE_PASS)

    blog_post = {
        "space": {'key': config.CONFLUENCE_SPACE},
        'type': 'blogpost',
        "title": "{} {}".format(title, project_name),
        'body': {
            'storage': {
                'representation': 'storage',
                'value': markdown(notes),
            }
        }
    }
    res = post(config.CONFLUENCE_API + "/content", auth=auth, json=blog_post)

    if res.status_code != 200:
        raise Exception("Blog post creation failed with: {}".res.content)

    content_url = res.json()["_links"]["self"]
    labels = [{"prefix": "global", "name": "release"},
              {"prefix": "global", "name": project_name.lower()}]

    res = post(content_url + "/label", auth=auth, json=labels)
    if res.status_code != 200:
        raise Exception("Blog post labelling failed: {}".res.content)


@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        validate_signature()

    except Exception:
        logger.exception("Refusing request, bad digest")
        abort(403)

    try:
        delivery = request.headers["X-GitHub-Delivery"]
        event = request.headers["X-GitHub-Event"]
        payload = request.get_json()

    except Exception:
        logger.exception("Invalid request")
        abort(400)

    logger.debug("Handling delivery: %s", delivery)
    if event == "release":
        release_published(payload["release"], payload["repository"])

    else:
        logger.warning("Unhandled event: %s(%s)", event, payload.get("action"))

    return ""


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    app.run(debug=True)
