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
START_ODDS = "odds on"
END_ODDS = "odds off"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
BOT_ON = False

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if 'type' not in event.keys():
            return None, None

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

def handle_command(command):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(START_ODDS):
        slack_client.rtm_send_message("general", "Turning Odds Notifications On")

        return True

    if command.startswith(END_ODDS):
        slack_client.rtm_send_message("general", "Turning Odds Notifications Off")
        return False

    return None


def create_messages_from_results(results):
    messages = []

    for (smarkets_url, oddschecker_url, event_results) in results:
        for horse, difference_obj in event_results.items():
            for bookie_name, bookie_odds_obj in difference_obj.items():
                profit = calculate_profit(bookie_odds_obj['smarkets'], bookie_odds_obj['odds_checker'])
                message = f"Profit: {profit} \n Bookie: {bookie_name}: \n diff: **{bookie_odds_obj['diff']}** \n smarkets: {bookie_odds_obj['smarkets']} \n lay: **{bookie_odds_obj['lay']}** \n oddschecker: {bookie_odds_obj['odds_checker']}\n"

                if profit > 0:
                    horse_message = f"Horse: **{horse}** \n "
                    messages.append(horse_message)
                    messages.append(message)
                    messages.append(f"Smarkets: {smarkets_url} \n Oddschecker: {oddschecker_url}")
                    messages.append("************")

    return messages


def get_odds():
    all_results = get_results()

    if all_results:
        messages = create_messages_from_results(all_results)
        for message in messages:
            slack_client.rtm_send_message("general", message)
        time.sleep(5)


def calculate_profit(smarkets_odd, odds_checker):
    return 0.98 * ((10 * odds_checker)/smarkets_odd-0.02) - 10


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            print("command:")
            print(command)
            if command:
                val = handle_command(command)
                print("Value")
                print(val)

                if val is not None:

                    if val is True:
                        BOT_ON = True
                        get_odds()
                    else:
                        BOT_ON = False
            else:
                if BOT_ON:
                    print("No Command But Getting Odds")

                    get_odds()
            time.sleep(1)
    else:
        print("Connection failed. Exception traceback printed above.")