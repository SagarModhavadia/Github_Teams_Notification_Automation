import pymsteams
import os
import logging
import json

import requests.exceptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

job_status = os.environ.get("STATUS")
job_name = os.environ.get("JOB_NAME")
workflow_name = os.environ.get("WORKFLOW_NAME")
facts = os.environ.get("FACTS")
repo_server_url = os.environ.get("REPO_SERVER_URL")
repo_name = os.environ.get("REPO_NAME")
hook_url = os.environ.get("WEBHOOK_URI")
triggering_actor = os.environ.get("TRIGGERING_ACTOR")
github_sha = os.environ.get("GITHUB_SHA")
run_id = os.environ.get("RUN_ID")


def send_sectioned_message():
    input_data = determine_input()
    # start the message
    teams_message = pymsteams.connectorcard(hook_url)
    teams_message.title(f"Workflow '{workflow_name}' {input_data['status']}")
    teams_message.text(f" ")

    # section 1
    section_1 = pymsteams.cardsection()
    section_1.activityTitle(f"Committed By: {triggering_actor}")
    section_1.activityTitle(f"Commit: {repo_server_url}/{repo_name}/commit/{github_sha}")
    # add link button
    teams_message.addLinkButton("Go to Action", f"{repo_server_url}/{repo_name}/actions/runs/{run_id}")

    # add facts
    for k, v in json.loads(facts).items():
        section_1.addFact(k, v)
    for k, v in dict({"Files Changed": f" ", "Workflow name": f"{workflow_name}"}).items():
        section_1.addFact(k, v)
    teams_message.addSection(section_1)
    teams_message.color(input_data["color"])
    # teams_message.printme()
    # send
    try:
        teams_message.send()
        evaluate_response(teams_message.last_http_response.status_code)
    except requests.exceptions.Timeout as te:
        logging.warning(te)
        logging.warning("The Teams notification will be skipped due to the timeout exception!!!")


def evaluate_response(resp_status_code):
    if isinstance(resp_status_code, int) and \
            0 <= resp_status_code <= 299:
        logging.info("Response code ok: %s", resp_status_code)
    else:
        logging.error("Unexpected response: %s", resp_status_code)
        raise ValueError(f"Unexpected response: '{resp_status_code}'")


def determine_input():
    msg = f"Job name: '{job_name}' of the workflow '{workflow_name}'"
    return {
        "iconUrl": "",
        "color": "2cc73b",
        "title": f"File changes committed!",
        "status": "succeeded"
    }
       
