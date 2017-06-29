version: "2"

services:
    wsgi-app:
        build: .

        command: uwsgi ./uwsgi.ini

        environment:
            GITHUB_WEBHOOK_SECRET: ""

            CONFLUENCE_API: ""
            CONFLUENCE_SPACE: ""
            CONFLUENCE_USER: ""
            CONFLUENCE_PASS: ""

            SLACK_WEBHOOK: ""
