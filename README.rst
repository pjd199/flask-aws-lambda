flask-aws-lambda
================

Python module to make Flask compatible with AWS Lambda for creating
RESTful applications. Compatible with both REST and HTTP API gateways.

Installation
------------

::

    pip install flask-aws-lambda

Usage
-----

This module works pretty much just like Flask. This allows you to run
and develop this applicaiton locally just like you would in Flask. When
ready deploy to Lambda, and configure the handler as:

::

    my_python_file.app

Here is an example of what ``my_python_file.py`` would look like:

.. code:: py

        import json
        from flask import request
        from flask_aws_lambda import FlaskAwsLambda


        app = FlaskAwsLambda(__name__)


        @app.route('/foo', methods=['GET', 'POST'])
        def foo():
            data = {
                'form': request.form.copy(),
                'args': request.args.copy(),
                'json': request.json
            }
            return (
                json.dumps(data, indent=4, sort_keys=True),
                200,
                {'Content-Type': 'application/json'}
            )

        if __name__ == '__main__':
            app.run(debug=True)

Flask-RESTful
-------------

Nothing special here, this module works without issue with Flask-RESTful
as well.

API Gateway
-----------

Configure your API Gateway with a ``{proxy+}`` resource with an ``ANY``
method. Your "Method Response" should likely include an
``application/json`` "Response Body for 200" that uses the ``Empty``
model.

Deploying
---------

Consider using `AWS Serverless Application Model (AWS
SAM) <https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html>`__.

Lambda Test Event
-----------------

If you wish to use the "Test" functionality in Lambda for your function,
you will need a "API Gateway AWS Proxy" event. Check the event JSON
objects in the `events <events/>`__ folder.

To update your test event, click "Actions" -> "Configure test event".
