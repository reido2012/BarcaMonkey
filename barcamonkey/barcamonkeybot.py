import os
import time
import re
from slackclient import SlackClient
from run import get_results, get_comparison_results

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# barcamonkeybot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def create_messages_from_results(results):
    messages = []

    for (smarkets_url, oddschecker_url, event_results) in results:
        message = ""
        for horse, difference_obj in event_results.items():
            horse_message = f"Horse: **{horse}** \n "
            message += horse_message
            for bookie_name, bookie_odds_obj in difference_obj.items():
                message += f"{bookie_name}: \n diff: **{bookie_odds_obj['diff']}** \n smarkets: {bookie_odds_obj['smarkets']} \n oddschecker: {bookie_odds_obj['odds_checker']}\n\n"

        message += f"Smarkets URL: {smarkets_url} \n Odds Checker URL: {oddschecker_url} \n "
        messages.append(message)

    return messages


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            time.sleep(30)
            all_results = get_results()
            messages = create_messages_from_results(all_results)
            for message in messages:
                slack_client.rtm_send_message("general", message)

    else:
        print("Connection failed. Exception traceback printed above.")