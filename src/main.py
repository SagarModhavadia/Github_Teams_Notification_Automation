import pymsteams
import os,requests, logging
import requests.exceptions
from github import Github, Auth
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

repo_server_url = os.environ.get("REPO_SERVER_URL")
repo_name = os.environ.get("REPO_NAME")
teams_channel_webhook_url = os.environ.get("TEAMS_CHANNEL_WEBHOOK_URL")
teams_channel_botflow_url = os.environ.get("TEAMS_CHANNEL_BOTFLOW_URL")
github_sha = os.environ.get("GITHUB_SHA")
github_token = os.environ.get("GITHUB_TOKEN")
run_id = os.environ.get("RUN_ID")
run_number = os.environ.get("RUN_NUMBER")
github_branch = os.environ.get("GITHUB_BRANCH")

def convert_utc_to_est(utc_datetime):
    est_timezone = pytz.timezone('America/New_York')
    est_datetime = utc_datetime.astimezone(est_timezone)
    return est_datetime.strftime(f"%m/%d/%Y %H:%M:%S %Z")

def send_teams_channel_message(notificationURL):
    auth = Auth.Token(f"{github_token}")
    github = Github(auth=auth)
    repo = github.get_repo(f"{repo_name}")
    commit = repo.get_commit(sha=f"{github_sha}")
    modifiedFiles = ""
    for file in commit.files:
        modifiedFiles += f"# [{file.filename}]({repo_server_url}/{repo_name}/blob/{github_branch}/{file.filename})\n"
    github.close()
    # start the message
    msTeams = pymsteams.connectorcard(notificationURL)
    msTeams.summary(f"Changes committed by {commit.author.name}")
    teams_message_section = pymsteams.cardsection()
    
    teams_message_section.activityTitle(f"CI #{run_number} | File changes committed on [{repo_name}]({repo_server_url}/{repo_name})")
    teams_message_section.activityImage(f"https://github.com/{commit.author.login}.png")
    teams_message_section.activityText(f"by [@{commit.author.login}](https://github.com/{commit.author.login}) on {convert_utc_to_est(commit.commit.author.date)}")
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

def replace_placeholder_values(source, values):
  # replaces all placeholders with values
  for k, v in values.items():
      placeholder = "$%s$" % k
      source = source.replace(placeholder, v)
  return source

def send_teams_bot_message(notificationURL):
    auth = Auth.Token(f"{github_token}")
    github = Github(auth=auth)
    repo = github.get_repo(f"{repo_name}")
    commit = repo.get_commit(sha=f"{github_sha}")
    modifiedFiles = ""
    for file in commit.files:
        modifiedFiles += f"[{file.filename}]({repo_server_url}/{repo_name}/blob/{github_branch}/{file.filename})\n\n "
    github.close()
    # start the bot message
    with open('src/resources/msteams_botflow_payload.txt') as payload_file:
        payload = payload_file.read()
        payload_mapping = {
            'GITHUB_RUN':f'CI #{run_number}',
            'IMAGE':f'https://github.com/{commit.author.login}.png',
            'IMAGE_ALT':f'{commit.author.login}', 
            'MESSAGE_HEADER': f'File changes committed on [{repo_name}]({repo_server_url}/{repo_name})',
            'MESSAGE_SUB_HEADER': f'by [{commit.author.login}](https://github.com/{commit.author.login}) on {convert_utc_to_est(commit.commit.author.date)}',
            'BRANCH': f'[{github_branch.upper()}]({repo_server_url}/{repo_name}/tree/{github_branch})',
            'COMMIT_MESSAGE': f'{commit.commit.message}',
            'FILES_CHANGED': f'{modifiedFiles}',
            'BTN_VIEW_STATUS': f'{repo_server_url}/{repo_name}/actions/runs/{run_id}',
            'BTN_VIEW_DIFFS': f'{repo_server_url}/{repo_name}/commit/{github_sha}'
        }
        final_payload = replace_placeholder_values(payload,payload_mapping)
        sendMessage = requests.post(notificationURL, final_payload)

if teams_channel_webhook_url:
    send_teams_channel_message(f"{teams_channel_webhook_url}")
if teams_channel_botflow_url:
    send_teams_bot_message(f"{teams_channel_botflow_url}")