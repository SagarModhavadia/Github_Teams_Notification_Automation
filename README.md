# Microsoft Teams Notification 
A GitHub Action that sends customizable notifications to a dedicated Microsoft Teams channel.

## Usage
1. Add `MS_TEAMS_WEBHOOK_URI` AND\OR `MS_TEAMS_BOT_FLOW_URI` on your repository's configs on Settings > Secrets. It is the [Webhook URI](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) of the dedicated Microsoft Teams channel or Groupchat for notification.

2) Add a belo `step` on workflow code:

```yaml
name: MS Teams Notification
on:
  push:
    branches: ['main']
jobs:
  send-msteams-notification:
    runs-on: ubuntu-latest
    name: Sends a notifications to MS Teams
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Notification
        if: always()
        id: send_notification
        uses: ./
        with:
          github_token: ${{ github.token }}
          #Use webhook url if you want to receive group notification 
          teams_channel_webhook_url: ${{ secrets.MS_TEAMS_WEBHOOK_URI }}
                        **OR**
          #Use botflow url if you want to receive group notification 
          teams_channel_botflow_url: ${{ secrets.MS_TEAMS_BOT_FLOW_URI }}

```

3. Make it your own with the following configurations.
   - `github-token` - (required), set to the following:
     - `${{ github.token }}`
   - `teams_channel_webhook_url` OR `teams_channel_botflow_url` - (required), setup a new secret to store your Microsoft Teams Webhook URI (ex. `MS_TEAMS_WEBHOOK_URI` OR `MS_TEAMS_BOT_FLOW_URI`). Learn more about setting up [GitHub Secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) or [Microsoft Teams Incoming Webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).
   
