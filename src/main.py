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
    msTeams = pymsteams.connectorcard(hook_url)
    msTeams.summary(f"Changes committed by {triggering_actor}")
    teams_message_section = pymsteams.cardsection()
    
    teams_message_section.activityTitle(f"File changes committed on [{repo_name}]({repo_server_url}/{repo_name})")
    teams_message_section.activityImage("https://cdn-icons-png.flaticon.com/512/2111/2111432.png")
    teams_message_section.activityText(f"by @[{triggering_actor}](https://github.com/{triggering_actor}) on ")
    # section 1
    teams_message_section.addFact("Commit message:", f" ")
    teams_message_section.addFact("Files changed:", f" ")
    # add link button
    msTeams.addLinkButton("View build/deploy status", f"{repo_server_url}/{repo_name}/actions/runs/{run_id}")
    msTeams.addLinkButton("Review commit diffs", f"{repo_server_url}/{repo_name}/commit/{github_sha}")
    
    msTeams.addSection(teams_message_section)
    msTeams.color("2cc73b")
    try:
        msTeams.send()
        evaluate_response(msTeams.last_http_response.status_code)
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