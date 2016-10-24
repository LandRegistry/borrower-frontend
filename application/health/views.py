from flask import Blueprint, render_template, jsonify
import requests
from application import config
import logging
from application.service.deed_api import interface
from application.service.deed_api import implementation

LOGGER = logging.getLogger(__name__)


health = Blueprint('health', __name__,
                   template_folder='/templates',
                   static_folder='static')


@health.route('/')
def health_main():
    return render_template('health.html')


@health.route('/service-check')
def service_check_routes():

    # Attempt to connect to deed-api which will attempt to connect to all
    # other services that are related to it.
    service_response = ""
    status_code = 500
    service_list = ""

    service_dict = {
        "status_code": status_code,
        "service_from": "borrower frontend",
        "service_to": "deed-api",
        "service_message": "Successfully connected"
    }

    try:
        # Create the interface that allows us to call the deed api's health route
        # and retrieve the response
        deed_api = interface.DeedApiInterface(implementation)
        service_response = deed_api.check_service_health()
        status_code = service_response.status_code
        service_list = service_response.json()

        # Add the success dict for Borrower Front End to the list of services
        # If there was an exception it would not get to this point
        service_dict["status_code"] = status_code
        service_list["services"].append(service_dict)

    # If a 500 error is reported, it will be far easier to determine the cause by
    # throwing an exception, rather than by getting an "unexpected error" output
    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        # A RequestException resolves the error that occurs when a connection cant be established
        # and the ValueError/TypeError exception may occur if the dict string / object is malformed
        status_code = 500
        LOGGER.error('A Request or Type/ValueError exception has occurred in get_service_check_response: %s', (e,), exc_info=True)

    if status_code != 200:
        # We either have a differing status code, add an error for this service
        # This would imply that we were not able to connect to deed-api
        service_dict["status_code"] = status_code
        service_dict["service_message"] = "Error: Could not connect"

        service_list = {
            "services":
            [
                service_dict
            ]
        }

    # Return the dict object containing the status of each service
    return jsonify(service_list)
