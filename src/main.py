import pymsteams
import os
import logging
import requests.exceptions
from github import Github
from github import Auth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

repo_server_url = os.environ.get("REPO_SERVER_URL")
repo_name = os.environ.get("REPO_NAME")
hook_url = os.environ.get("WEBHOOK_URI")
github_sha = os.environ.get("GITHUB_SHA")
github_token = os.environ.get("GITHUB_TOKEN")
run_id = os.environ.get("RUN_ID")
run_number = os.environ.get("RUN_NUMBER")
github_branch = os.environ.get("GITHUB_BRANCH")

def send_teams_message():
    auth = Auth.Token(f"{github_token}")
    github = Github(auth=auth)
    repo = github.get_repo(f"{repo_name}")
    commit = repo.get_commit(sha=f"{github_sha}")
    print(f"Commit::: {commit}")
    modifiedFiles = ""
    for file in commit.files:
        modifiedFiles += f"# [{file.filename}]({repo_server_url}/{repo_name}/blob/main/{file.filename})\n"
    github.close()

    # start the message
    msTeams = pymsteams.connectorcard(hook_url)
    msTeams.summary(f"Changes committed by {commit.committer.name}")
    teams_message_section = pymsteams.cardsection()
    
    teams_message_section.activityTitle(f"CI #{run_number} | File changes committed on [{repo_name}]({repo_server_url}/{repo_name})")
    teams_message_section.activityImage("https://cdn-icons-png.flaticon.com/512/2111/2111432.png")
    teams_message_section.activityText(f"by [@{commit.committer.name}](https://github.com/{commit.committer.name}) on {commit.last_modified}")
    # section 1
    teams_message_section.addFact("Branch:", f"[{github_branch.upper()}]({repo_server_url}/{repo_name}/tree/{github_branch})")
    teams_message_section.addFact("Commit message:", f"{commit.commit.message}")
    teams_message_section.addFact("Files changed:", f"{modifiedFiles}")
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
    
send_teams_message()