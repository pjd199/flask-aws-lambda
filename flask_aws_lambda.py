# -*- coding: utf-8 -*-
# Copyright 2021 Nik Ho
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import sys
from io import BytesIO, StringIO
from typing import Any, Dict
from urllib.parse import urlencode

from flask import Flask
from werkzeug.wrappers import Request

__version__ = "1.0.2"


def make_wsgi_environ() -> Dict[str, Any]:
    """Contruct default environs object."""
    return {
        "HTTP_HOST": "",
        "HTTP_X_FORWARDED_PORT": "",
        "HTTP_X_FORWARDED_PROTO": "",
        "SCRIPT_NAME": "",
        "wsgi.version": (1, 0),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.run_once": True,
        "wsgi.multiprocess": False,
    }


def make_v1_environ(event: Dict[str, Any], environ: Dict[str, Any]):
    """
    Create environ object from REST API Gateway event.

    Note: This function mutates the incoming eviron object.
    """
    qs = event["queryStringParameters"] if "queryStringParameters" in event else None
    environ["REQUEST_METHOD"] = event["httpMethod"]
    environ["PATH_INFO"] = event["path"]
    environ["QUERY_STRING"] = urlencode(qs) if qs else ""
    environ["REMOTE_ADDR"] = event["requestContext"]["identity"]["sourceIp"]
    environ["SERVER_PROTOCOL"] = event["requestContext"]["protocol"]


def make_v2_environ(event: Dict[str, Any], environ: Dict[str, Any]):
    """
    Create environ object from HTTP API Gateway event.

    Note: This function mutates the incoming eviron object.
    """
    qs = event["queryStringParameters"] if "queryStringParameters" in event else None
    environ["REQUEST_METHOD"] = event["requestContext"]["http"]["method"]
    environ["PATH_INFO"] = event["requestContext"]["http"]["path"]
    environ["QUERY_STRING"] = urlencode(qs) if qs else ""
    environ["REMOTE_ADDR"] = event["requestContext"]["http"]["sourceIp"]
    environ["SERVER_PROTOCOL"] = event["requestContext"]["http"]["protocol"]


def make_environ(event: Dict[str, Any]):
    # get the standard base set of environ properties
    environ = make_wsgi_environ()

    # set headers from event
    if event["headers"] is not None:
        for hdr_name, hdr_value in event["headers"].items():
            hdr_name = hdr_name.replace("-", "_").upper()
            if hdr_name in ["CONTENT_TYPE", "CONTENT_LENGTH"]:
                environ[hdr_name] = hdr_value
                continue
            # prefix HTTP to all other headers
            http_hdr_name = "HTTP_%s" % hdr_name
            environ[http_hdr_name] = hdr_value

    # make environ specifically from REST or HTTP gateway events
    # the properties of the event object is slightly different in both gateways
    if event["version"] == "1.0":
        make_v1_environ(event, environ)
    else:
        make_v2_environ(event, environ)

    # add the port and protocol
    environ["SERVER_PORT"] = environ["HTTP_X_FORWARDED_PORT"]
    environ["wsgi.url_scheme"] = environ["HTTP_X_FORWARDED_PROTO"]

    # add the body, if there is one, and base64 decode if needed
    if "body" in event:
        if event["isBase64Encoded"]:
            body = base64.b64decode(event["body"])
            environ["CONTENT_LENGTH"] = str(len(body))
            environ["wsgi.input"] = BytesIO(body)
        else:
            environ["CONTENT_LENGTH"] = str(len(event["body"]))
            environ["wsgi.input"] = StringIO(event["body"])
    else:
        environ["CONTENT_LENGTH"] = ""
        environ["wsgi.input"] = ""

    # using werkzeug.wrappers.Request instead of BaseRequest
    # as BaseRequest has a deprecation warning for next version
    Request(environ)

    return environ


class LambdaResponse:
    def __init__(self):
        self.status = None
        self.response_headers = None

    def start_response(self, status, response_headers, exc_info=None) -> None:
        self.status = int(status[:3])
        self.response_headers = dict(response_headers)


class FlaskAwsLambda(Flask):
    def __call__(self, event, context):
        if "version" not in event:
            # In this "context" `event` is `environ` and
            # `context` is `start_response`, meaning the request didn't
            # occur via API Gateway and Lambda
            return super(FlaskAwsLambda, self).__call__(event, context)

        response = LambdaResponse()

        # b''.join = fix for next stopIterator error
        # https://github.com/sivel/flask-lambda/pull/10/files
        body = b"".join(self.wsgi_app(make_environ(event), response.start_response))

        lamdba_response = {
            "statusCode": response.status,
            "headers": response.response_headers,
            "body": body,
            "isBase64Encoded": False,
        }

        if response.response_headers is not None:
            content_type = response.response_headers["Content-Type"]
            if (
                "text" not in content_type
                and "json" not in content_type
                and "xml" not in content_type
                and "javascript" not in content_type
                and "charset=" not in content_type
            ):
                lamdba_response["body"] = base64.b64encode(body).decode("utf-8")
                lamdba_response["isBase64Encoded"] = True

        return lamdba_response
