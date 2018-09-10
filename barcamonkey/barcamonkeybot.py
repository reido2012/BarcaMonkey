import os
import time
import re
import traceback
import pytz
import sys
from datetime import datetime, timedelta
from slackclient import SlackClient
from run import get_results, get_comparison_results
from twilio.rest import Client

TZ = pytz.timezone('Europe/London')
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
                qb_profit = bookie_odds_obj['qb_profit']
                fb_profit = bookie_odds_obj['fb_profit']
                high_qb = bookie_odds_obj['high_qb']

                if high_qb:
                    make_call(os.environ.get('ADAM_MOBILE'))
                    high_qb_msg = "HIGHQB"

                smarkets_odds = round(bookie_odds_obj['smarkets'], 2)
                oddschecker_odds = round(bookie_odds_obj['odds_checker'], 2)
                message = f"Bookie: *{bookie_name}* \n QB Profit: *£{qb_profit}* \n FB Profit: £{fb_profit} \n Odds: *{oddschecker_odds} - {smarkets_odds}* \n Lay: {bookie_odds_obj['lay']} \n"

                str_msg_temp.append(message)

                if high_qb:
                    str_msg_temp.append(f"Priority: {high_qb_msg} \n")

                location, race_time = parse_smarkets_url(smarkets_url)
                str_msg_temp.append(f"Race: {race_time} {location.capitalize()} \n")
                time_obj = datetime.now(TZ).time()
                msg_time = '{:02d}'.format(time_obj.hour) + ":" + '{:02d}'.format(time_obj.minute)
                str_msg_temp.append(f"Msg Time: {msg_time} \n")
                str_msg_temp.append("*********************\n")

            if str_msg_temp:
                messages.append(f"Horse: *{horse}* \n " + " ".join(str_msg_temp))

    print(f"Messages: {messages}")
    return messages


def make_call(phone_number):
    account_sid = os.environ.get('TWILIO_ACC_SID')
    auth_token = os.environ.get('TWILIO_AUTH')

    client = Client(account_sid, auth_token)

    call = client.calls.create(
                            url='http://demo.twilio.com/docs/voice.xml',
                            to=phone_number,
                            from_='+447492885157'
                        )

    print(call.sid)


def parse_smarkets_url(url):
    split_url = url.split("/")
    return split_url[7], split_url[11]


def get_odds():
    all_results = get_results()
    print(all_results)
    if all_results == 0:
        slack_client.rtm_send_message("general", "An Error Has Ocurred")
        sys.exit(0)

    if all_results:
        messages = create_messages_from_results(all_results)
        for message in messages:
            slack_client.rtm_send_message("general", message)
        time.sleep(5)


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

            prev_command = ""
            while True:
                command, channel = parse_bot_commands(slack_client.rtm_read())

                if command not in [START_ODDS, END_ODDS]:
                    command = ""

                if command == "":
                    run_command(prev_command)
                else:
                    prev_command = command
                    run_command(command)

                time.sleep(1)

        else:
            print("Connection failed. Exception traceback printed above.")

    except Exception as e:
        traceback.print_exc()
