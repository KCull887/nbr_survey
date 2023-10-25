
import requests
import json


def run_request(content, oConnection, addl_options=None):
    if addl_options is None:
        addl_options = {}
    addl_options['content'] = content
    addl_options['token'] = oConnection.get_api_token()
    addl_options['format'] = 'json'
    addl_options['returnFormat'] = 'json'
    # print("query", addl_options)
    return requests.post(oConnection.api_url.url, addl_options).json()

def get_next_instance_number(oConnection, oInstrument, record_id):
    """
    Look in REDCap to find what the next instance should be for the specified instrument/record_id
    """
    options = {
        'records[0]': str(record_id),
        'forms[1]': oInstrument.instrument_name,
        'fields[1]': 'record_id',
        'events[0]': 'all_measures_arm_1',
    }
    response = run_request("record", oConnection, options)
    max_instance = 0
    for entry in response:
        instance_string = entry["redcap_repeat_instance"]
        if instance_string:
            instance = int(instance_string)
            if instance > max_instance:
                max_instance = instance
    return max_instance + 1

def delete_instrument(oConnection, record_id, instrument_name, repeat_instance):
    options = {
        "action": "delete",
        "records[0]": str(record_id),
        "event": "all_measures_arm_1",
        "instrument": instrument_name,
        "repeat_instance": repeat_instance,
    }
    response = run_request("record", oConnection, options)
    if str(response) == "1":
        return True
    return False

def create_instrument(oConnection, oInstrument, record_id, visit_date):
    instance = get_next_instance_number(oConnection, oInstrument, record_id)
    data = {
        "record_id": str(record_id),
        "redcap_event_name": "all_measures_arm_1",
        "redcap_repeat_instrument": oInstrument.instrument_name,
        "redcap_repeat_instance": str(instance),
        # "redcap_repeat_instance": "new",
        # we need to define at least one field from the instrument or we'll get a cryptic error
        oInstrument.instrument_field: str(visit_date),
    }
    upload_data = [data]
    upload_data = json.dumps(upload_data)
    response = run_request("record", oConnection, {"data": upload_data})
    return instance, response

