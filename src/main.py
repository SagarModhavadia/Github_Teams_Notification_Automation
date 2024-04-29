import pymsteams
import os
import logging

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
    # start the message
    teams_message = pymsteams.connectorcard(hook_url)
    teams_message.activityTitle(f"File changes committed on [{repo_server_url}/{repo_name}]({repo_server_url}/{repo_name})")
    teams_message.activityImage("http://www.clker.com/cliparts/v/u/z/w/n/2/thumbsup-md.png")
    teams_message.activityText(f"by @[{triggering_actor}](https://github.com/{triggering_actor}) on ")
    # section 1
    section_1 = pymsteams.cardsection()
    section_1.addFact("Committed by:", )
    section_1.addFact("Commit message:", f" ")
    section_1.addFact("Files changed:", f" ")
    # add link button
    teams_message.addLinkButton("View build/deploy status", f"{repo_server_url}/{repo_name}/actions/runs/{run_id}")
    teams_message.addLinkButton("Review commit diffs", f"{repo_server_url}/{repo_name}/commit/{github_sha}")
    
    teams_message.addSection(section_1)
    teams_message.color("2cc73b")
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
    
send_sectioned_message()