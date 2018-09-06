import os
import time
import re
import traceback
from slackclient import SlackClient
from run import get_results, get_comparison_results
from collections import deque

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
        slack_client.rtm_send_message(channel, "Turning Odds Notifications On")
        return True

    if command.startswith(END_ODDS):
        slack_client.rtm_send_message(channel, "Turning Odds Notifications Off")
        return False

    return None


def create_messages_from_results(results):
    messages = []
    for (smarkets_url, oddschecker_url, event_results) in results:
        for horse, difference_obj in event_results.items():
            str_msg_temp = []
            for bookie_name, bookie_odds_obj in difference_obj.items():
                qb_profit = qualifying_bet_profit(bookie_odds_obj['smarkets'], bookie_odds_obj['odds_checker'])
                fb_profit = free_bet_profit(bookie_odds_obj['smarkets'], bookie_odds_obj['odds_checker'])

                smarkets_odds = round(bookie_odds_obj['smarkets'], 2)
                oddschecker_odds = round(bookie_odds_obj['odds_checker'], 2)
                message = f"Bookie: *{bookie_name}* \n QB Profit: *£{qb_profit}* \n Smarkets: {smarkets_odds} \n Lay: {bookie_odds_obj['lay']} \n Oddschecker: {oddschecker_odds} \n FB Profit: £{fb_profit} \n "

                if (qb_profit > 0.1) or (fb_profit >= 12):
                    str_msg_temp.append(message)
                    location, race_time = parse_smarkets_url(smarkets_url)
                    str_msg_temp.append(f"Location: {location} \n Time: {race_time} \n")
                    str_msg_temp.append("*********************")

            if str_msg_temp:
                messages.append(f"Horse: *{horse}* \n " + " ".join(str_msg_temp))

    print(f"Messages: {messages}")
    return messages


def parse_smarkets_url(url):
    split_url = url.split("/")
    return split_url[7], split_url[11]


def get_odds():
    all_results = get_results()
    print(f"All Results: {all_results}")

    if all_results == 0:
        slack_client.rtm_send_message("general", "An Error Has Ocurred")

    if all_results:
        messages = create_messages_from_results(all_results)
        for message in messages:
            slack_client.rtm_send_message("general", message)
        time.sleep(5)


def qualifying_bet_profit(smarkets_odd, odds_checker):
    return round((0.98 * ((10 * odds_checker)/smarkets_odd-0.02) - 10), 2)


def free_bet_profit(smarkets_odd, odds_checker):
    return round(((10*(odds_checker-1)) / (smarkets_odd-0.02)), 2)


def run_command(command):
    val = handle_command(command)

    if val is not None:

        if val is True:
            get_odds()
            return True
        else:
            return False


if __name__ == "__main__":
    try:
        if slack_client.rtm_connect():
            print("Starter Bot connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
            starterbot_id = slack_client.api_call("auth.test")["user_id"]
            command_queue = deque([])
            while True:
                command, channel = parse_bot_commands(slack_client.rtm_read())

                if command not in [START_ODDS, END_ODDS, None]:
                    command = None

                if command in [START_ODDS, END_ODDS]:
                    command_queue.append(command)

                if command:
                    command = command_queue.popleft()
                    BOT_ON = run_command(command)
                else:
                    if len(command_queue) > 0:
                        command = command_queue.popleft()
                        BOT_ON = run_command(command)
                    else:
                        if BOT_ON:
                            print("No Command But Getting Odds")
                            BOT_ON = run_command(START_ODDS)
                            
                time.sleep(1)

        else:
            print("Connection failed. Exception traceback printed above.")

    except Exception as e:
        traceback.print_exc()
