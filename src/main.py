import pymsteams
import os
import logging
import requests.exceptions
from github import Github
from github import Auth
import adaptive_cards.card_types as types
from adaptive_cards.actions import ActionToggleVisibility, TargetElement
from adaptive_cards.validation import SchemaValidator, Result
from adaptive_cards.card import AdaptiveCard
from adaptive_cards.elements import TextBlock, Image
from adaptive_cards.containers import Container, ContainerTypes, ColumnSet, Column
import requests

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
    containers: list[ContainerTypes] = []
    icon_source: str = "https://icons8.com/icon/vNXFqyQtOSbb/launch"
    icon_url: str = "https://img.icons8.com/3d-fluency/94/launched-rocket.png"

    header_column_set: ColumnSet = ColumnSet(
        columns=[
            Column(
                items=[
                    TextBlock(text="Your Daily Wrap-Up", size=types.FontSize.EXTRA_LARGE)
                ],
                width="stretch",
            ),
            Column(items=[Image(url=icon_url, width="40px")], rtl=True, width="auto"),
        ]
    )
    containers.append(
        Container(
            items=[header_column_set], style=types.ContainerStyle.EMPHASIS, bleed=True
        )
    )

    containers.append(
        Container(
            items=[
                TextBlock(
                    text="**Some numbers for you**",
                    size=types.FontSize.MEDIUM,
                ),
                ColumnSet(
                    columns=[
                        Column(
                            items=[
                                TextBlock(text="_Total_"),
                                TextBlock(text="_Done by you_"),
                                TextBlock(text="_Done by other teams_"),
                                TextBlock(text="_Still open_"),
                                TextBlock(text="_Closed_"),
                            ]
                        ),
                        Column(
                            items=[
                                TextBlock(text="5"),
                                TextBlock(text="4"),
                                TextBlock(text="3"),
                                TextBlock(text="6"),
                                TextBlock(text="1"),
                            ],
                            spacing=types.Spacing.MEDIUM,
                            rtl=True,
                        ),
                    ],
                    separator=True,
                ),
            ],
            spacing=types.Spacing.MEDIUM,
        )
    )

    containers.append(
        Container(
            items=[
                TextBlock(
                    text="**Detailed Results**",
                    size=types.FontSize.MEDIUM,
                ),
            ],
            separator=True,
            spacing=types.Spacing.EXTRA_LARGE,
        )
    )

    sample_column_set: ColumnSet = ColumnSet(
        columns=[
            Column(items=[TextBlock(text="12312")]),
            Column(items=[TextBlock(text="done", color=types.Colors.GOOD)]),
            Column(items=[TextBlock(text="abc")]),
            Column(
                items=[
                    Image(
                        url="https://adaptivecards.io/content/down.png",
                        width="20px",
                        horizontal_alignment=types.HorizontalAlignment.RIGHT,
                    )
                ],
                select_action=ActionToggleVisibility(
                    title="More",
                    target_elements=[
                        TargetElement(
                            element_id="toggle-me",
                        )
                    ],
                ),
            ),
        ]
    )

    containers.append(
        Container(
            items=[
                Container(
                    items=[
                        ColumnSet(
                            columns=[
                                Column(items=[TextBlock(text="**Number**")]),
                                Column(items=[TextBlock(text="**Status**")]),
                                Column(items=[TextBlock(text="**Topic**")]),
                                Column(items=[TextBlock(text="")]),
                            ],
                            id="headline",
                        ),
                    ],
                    style=types.ContainerStyle.EMPHASIS,
                    bleed=True,
                ),
                Container(items=[sample_column_set]),
                Container(
                    items=[
                        TextBlock(
                            text="_Here you gonna find more information about the whole topic_",
                            id="toggle-me",
                            is_visible=False,
                            is_subtle=True,
                            wrap=True,
                        )
                    ]
                ),
            ],
        )
    )

    containers.append(
        Container(
            items=[
                TextBlock(
                    text=f"Icon used from: {icon_source}",
                    size=types.FontSize.SMALL,
                    horizontal_alignment=types.HorizontalAlignment.CENTER,
                    is_subtle=True,
                )
            ]
        )
    )

    card = AdaptiveCard.new().version("1.5").add_items(containers).create()

    validator: SchemaValidator = SchemaValidator()
    result: Result = validator.validate(card)
    sendMessage = requests.post(notificationURL, json = card.to_json())
    
send_teams_channel_message(f"{hook_url}")
send_teams_bot_message(f"https://prod-143.westus.logic.azure.com:443/workflows/b4c5c338f1204fd996fb3579b554c947/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pbPqwQbiTHFepQusyNQVW6DME2xRTLLLKNyNoB1eh7k")