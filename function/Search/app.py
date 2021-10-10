import os
from slack_bolt import App
import json
import logging
from cause_functions import SearchCause, CauseEncoder, Generic, CauseHelper

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True # must be True when running on FaaS
)

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

@app.command("/share")
def give_causes(ack, command, respond):
    ack()
    edited_command = command['text'].replace(' ', '%20')

    # getting list_of_causes
    logging.debug("Creating a cause_helper object")
    cause_obj = CauseHelper(edited_command, 0)
    global list_of_causes
    list_of_causes = cause_obj.get_list_of_causes(edited_command)

    # printing message
    result = get_cause(respond, edited_command, 0)
    # say("I am here after sending the message in slack.")

    logging.info('I am here after sending the message in slack.')
    global text
    text = edited_command

    global cause_search_dto_global
    cause_search_dto_global = result

@app.action("button_send")
def send_message_final(ack, say, respond):
    ack()
    result=get_cause_final(say)
    delete_prev_msg(respond)

@app.action("button_next")
def get_next_cause(ack, respond):
    ack()
    global i
    i+=1
    next_cause = get_cause(respond, text, i)
    global cause_search_dto_global
    # stores cause_search_dto
    cause_search_dto_global = next_cause

@app.action("button_cancel")
def close_message(ack, respond):
    ack()
    respond(
        response_type= "in_channel",
        replace_original=False,
        delete_original=True
    )

@app.action("view_alternate_1")
def give_first_alternate(ack, respond): # ,client
    ack()
    respond(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": 'mrkdwn',
                    "text": "<" + second_mygoodness_url + "|*" + second_name_global + "*>\n" + second_result
                }
            }
        ]
    )

@app.action("view_alternate_2")
def give_second_alternate(ack, client):
    ack()
    client.chat_postEphemeral(
        channel="C023FN6ADTN",
        user="U0239H8QHEE",
        attachments=[{
            "prextext": "nothing",
            "text": "<" + third_mygoodness_url + "|*" + third_name_global + "*>\n" + third_result
        }],
        text="More Info:"
    )

@app.action("exit_button")
def exit_search(ack, respond):
    ack()
    delete_prev_msg(respond)

# deletes the previous message
def delete_prev_msg(respond):
    respond(
        response_type= "in_channel",
        replace_original=False,
        delete_original=True
    )


def get_causes(say, command_text):
    edited_command = command_text.replace( ' ', '%20')
    i = 0
    if SearchCause(edited_command).return_cause(edited_command):
        lst_of_causes = SearchCause(edited_command).return_cause(edited_command)
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Causes:*"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        )
        for causes in lst_of_causes:
            if i < 5 and i < len(lst_of_causes):
                result = ''
                causeJson = json.dumps(causes, indent = 4, cls=CauseEncoder)
                cause = json.loads(causeJson, object_hook=Generic.from_dict)
                mygoodness_url = 'https://mygoodness.benevity.org/en-ca/cause/' + cause.id
                result += '*ID:* ' + cause.id + '\n*Location:* ' + cause.attributes.city + ', ' + cause.attributes.state.name
                i += 1

                say(
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "<" + mygoodness_url + "|*" + cause.attributes.name + "*>\n" + result
                            }
                        }
                    ]
                )
        say(
            blocks=[
                {
                    "type": "divider"
                }
            ]
        )
    else:
        say("No results found.")

def get_cause(respond, command_text, idx):
    logging.info("The search command received: {}".format(text))
    try:
        cause = CauseHelper(command_text, idx)
        cause_search_dto = cause.search_cause(list_of_causes, idx)
        # try:
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
                },
            ]
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
                        "action_id": "exit_button",
                    }
                },
            ]
        )
    return cause_search_dto

def get_cause_final(say):
    # logging.info("The search command received: {}".format(command_text))
    try:
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
            ]
        )
    except:
        say("No results found.")

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))