import pymsteams
import os
import logging
import requests.exceptions
from github import Github
from github import Auth
from adaptivecards.adaptivecard import AdaptiveCard
from adaptivecards.elements import TextBlock
from adaptivecards.containers import Column, ColumnSet, Container

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

repo_server_url = os.environ.get("REPO_SERVER_URL")
repo_name = os.environ.get("REPO_NAME")
hook_url = os.environ.get("WEBHOOK_URI")
github_sha = os.environ.get("GITHUB_SHA")
github_token = os.environ.get("GITHUB_TOKEN")
run_id = os.environ.get("RUN_ID")
run_number = os.environ.get("RUN_NUMBER")
github_branch = os.environ.get("GITHUB_BRANCH")

def send_teams_channel_message(notificationURL):
    auth = Auth.Token(f"{github_token}")
    github = Github(auth=auth)
    repo = github.get_repo(f"{repo_name}")
    commit = repo.get_commit(sha=f"{github_sha}")
    modifiedFiles = ""
    for file in commit.files:
        modifiedFiles += f"# [{file.filename}]({repo_server_url}/{repo_name}/blob/main/{file.filename})\n"
    github.close()
    # start the message
    msTeams = pymsteams.connectorcard(notificationURL)
    msTeams.summary(f"Changes committed by {commit.committer.name}")
    teams_message_section = pymsteams.cardsection()
    
    teams_message_section.activityTitle(f"CI #{run_number} | File changes committed on [{repo_name}]({repo_server_url}/{repo_name})")
    teams_message_section.activityImage("https://cdn-icons-png.flaticon.com/512/2111/2111432.png")
    teams_message_section.activityText(f"by [@{commit.committer.login}](https://github.com/{commit.committer.login}) on {commit.last_modified}")
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

def send_teams_bot_message(notificationURL):
    auth = Auth.Token(f"{github_token}")
    github = Github(auth=auth)
    repo = github.get_repo(f"{repo_name}")
    commit = repo.get_commit(sha=f"{github_sha}")
    modifiedFiles = ""
    for file in commit.files:
        modifiedFiles += f"# [{file.filename}]({repo_server_url}/{repo_name}/blob/main/{file.filename})\n"
    github.close()
    # start the message
    card = AdaptiveCard()
    card.version="1.4"
    card.body = [
        Container(items=[
            TextBlock(text='Hello from adaptivecards', font_type='Default', size='Medium'),
            ColumnSet(columns=[
                Column(
                    width='stretch',
                    items=[
                        TextBlock(text='author', weight="Bolder", wrap=True),
                        TextBlock(text='version', weight="Bolder", wrap=True),
                    ]
                ),
                Column(
                    width='stretch',
                    items=[
                        TextBlock(text='Huu Hoa NGUYEN', wrap=True),
                        TextBlock(text='0.1.0', wrap=True),
                    ]
                )
            ])
        ]),
        TextBlock(text='more information can be found at [https://pypi.org/project/adaptivecards/](https://pypi.org/project/adaptivecards/)',
                wrap=True)
    ]
    json_str = str(card)
    print(json_str)
send_teams_channel_message(f"{hook_url}")
send_teams_bot_message(f"https://prod-143.westus.logic.azure.com:443/workflows/b4c5c338f1204fd996fb3579b554c947/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pbPqwQbiTHFepQusyNQVW6DME2xRTLLLKNyNoB1eh7k")