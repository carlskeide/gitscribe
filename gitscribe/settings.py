# coding=utf-8
from os import environ as env


class FlaskConfig(object):
    DEBUG = False


# Secrets
WEBHOOK_SECRET = env.get("GITHUB_WEBHOOK_SECRET").encode('utf-8')

SLACK_WEBHOOK = env.get("SLACK_WEBHOOK")

CONFLUENCE_API = env.get("CONFLUENCE_API")
CONFLUENCE_SPACE = env.get("CONFLUENCE_SPACE")
CONFLUENCE_USER = env.get("CONFLUENCE_USER")
CONFLUENCE_PASS = env.get("CONFLUENCE_PASS")


# Styling
RELEASE_NAME = "{title} {project}"
