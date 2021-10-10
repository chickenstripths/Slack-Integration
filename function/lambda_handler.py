import logging
import sys
sys.path.insert(1, "vendor")
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from function.Search.cause_functions import CauseHelper

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(":x: Usage: /share (description here)")
    else:
        ack()

def give_causes(command, respond):
    edited_command = command['text'].replace(' ', '%20')

    cause_obj = CauseHelper(edited_command, 0)
    global list_of_causes
    list_of_causes = cause_obj.get_list_of_causes(edited_command)

    result = get_cause(respond, edited_command, 0)

    global text
    text = edited_command

    global cause_search_dto_global
    cause_search_dto_global = result

# Global Variables
text = ""
i = 0
second_name_global = ""
second_result = ""
second_mygoodness_url = ""
third_name_global = ""
third_result = ""
third_mygoodness_url = ""
cause_search_dto_global = None
global_result = ""
list_of_causes = []

app.command("/share")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[give_causes]
)

@app.action("button_send")
def send_message_final(ack, say, respond):
    ack()
    result=get_cause_final(say)
    delete_prev_msg(respond)
    global i
    i = 0

@app.action("button_next")
def get_next_cause(ack, respond):
    ack()
    global i
    i += 1
    next_cause = get_cause(respond, text, i)
    global cause_search_dto_global
    # stores cause_search_dto
    cause_search_dto_global = next_cause

@app.action("button_cancel")
def close_message(ack, respond):
    ack()
    delete_prev_msg(respond)
    global i
    i = 0

def get_cause(respond, command_text, idx):
    cause = CauseHelper(command_text, idx)
    cause_search_dto = cause.search_cause(list_of_causes, idx)

    try:
        respond(
            blocks=[
                {
                    "type": 'section',
                    "text": {
                        "type": 'mrkdwn',
                        "text": "<" + cause_search_dto.mygoodness_url + "|*" + cause_search_dto.first_name_global + "*>\n" +
                                cause_search_dto.description
                    },
                },
                {
                    "type": "image",
                    "image_url": cause_search_dto.logo,
                    "alt_text": "Logo"
                },
                {
                    "type": 'section',
                    "text": {
                        "type": 'mrkdwn',
                        "text": cause_search_dto.location
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Send"
                            },
                            "style": "primary",
                            "action_id": "button_send"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Next Cause",
                            },
                            "action_id": "button_next"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Cancel"
                            },
                            "action_id": "button_cancel"
                        }
                    ]
                }
            ],
        )
        return cause_search_dto
    except:
        edited_command = command_text.replace('%20',' ')
        respond(
            blocks=[
                {
                    "type": 'section',
                    "text": {
                        "type": 'mrkdwn',
                        "text": "No results found for *" + edited_command + ".*"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "exit"
                        },
                        "action_id": "button_cancel",
                    }
                },
            ]
        )
    return cause_search_dto

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

def get_cause_final(say):
    # logging.info("The search command received: {}".format(command_text))
    say(
        blocks=[
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": "<" + cause_search_dto_global.mygoodness_url + "|*" +
                            cause_search_dto_global.first_name_global + "*>\n" +
                            cause_search_dto_global.description
                },
            },
            {
                "type": "image",
                "image_url": cause_search_dto_global.logo,
                "alt_text": "Logo"
            },
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": cause_search_dto_global.location
                }
            }
        ],
    )

def delete_prev_msg(respond):
    respond(
        response_type= "in_channel",
        replace_original=False,
        delete_original=True
    )

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)