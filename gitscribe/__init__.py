#!/usr/bin/env python3
# coding=utf-8
import logging
import hmac

from flask import Flask, request, abort
from requests import post
from markdown import markdown

from . import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(settings.FlaskConfig)


def validate_signature():
    logger.debug("Validating request digest")

    mode, digest = request.headers["X-Hub-Signature"].split('=')
    real_hmac = hmac.new(settings.WEBHOOK_SECRET, request.data, mode)
    if not hmac.compare_digest(digest, real_hmac.hexdigest()):
        raise ValueError("Invalid HMAC")


def release_published(release, repo):
    logger.debug("New release: %s", release["tag_name"])

    project = repo["name"].title()
    title = release["tag_name"]
    if release["body"]:
        notes = release["body"]

    else:
        logger.warning("Empty release notes")
        notes = "No release notes."

    if settings.CONFLUENCE_API:
        Update_confluence(title, notes, project)

    if settings.SLACK_WEBHOOK:
        notify_slack(title, notes, project)


def Update_confluence(title, notes, project):
    logger.info("Creating confluence relase notes for: %s", title)

    auth = (settings.CONFLUENCE_USER, settings.CONFLUENCE_PASS)

    blog_post = {
        "space": {'key': settings.CONFLUENCE_SPACE},
        'type': 'blogpost',
        "title": settings.RELEASE_NAME.format(title=title, project=project),
        'body': {
            'storage': {
                'representation': 'storage',
                'value': markdown(notes),
            }
        }
    }
    res = post(settings.CONFLUENCE_API + "/content", auth=auth, json=blog_post)

    if res.status_code != 200:
        raise Exception("Blog post creation failed with: {}".format(res.content))

    content_url = res.json()["_links"]["self"]
    labels = [{"prefix": "global", "name": "release"},
              {"prefix": "global", "name": project.lower()}]

    res = post(content_url + "/label", auth=auth, json=labels)
    if res.status_code != 200:
        raise Exception("Blog post labelling failed: {}".format(res.content))


def notify_slack(title, notes, project):
    logger.info("Notifying slack about relase: %s", title)

    long_title = settings.RELEASE_NAME.format(title=title, project=project)
    payload = {
        'color': '#439FE0',
        'fallback': "New release notes: {}".format(long_title),
        "pretext": "New release notes have been published",
        'title': long_title,
        'fields': [
            {
                'title': 'Release notes',
                'value': notes,
                'short': False
            }
        ],
        'mrkdwn_in': ['text', 'fields']
    }

    res = post(settings.SLACK_WEBHOOK, json={"attachments": [payload, ]})
    if res.status_code != 200:
        raise Exception("Slack notification failed: {}".format(res.content))


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
