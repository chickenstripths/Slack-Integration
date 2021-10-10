import json
import logging
from cause_functions import SearchCause, CauseEncoder, Generic
from app import text, i, second_name_global, second_result, second_mygoodness_url, third_name_global, third_result, third_mygoodness_url

class GetCause:
    def __init__(self, command_text, idx):
        self.command_text = command_text
        self.idx = idx
    def get_cause(self, respond):
        # Acknowledge command request
        logging.info("The search command received: {}".format(self.command_text))
        edited_command = self.command_text.replace( ' ', '%20')
        # if SearchCause(edited_command).return_cause(edited_command):
        try:
            lst_of_causes = SearchCause(edited_command).return_cause(edited_command)
            cause_at_idx = lst_of_causes[self.idx]
            causeJson = json.dumps(cause_at_idx, indent=4, cls=CauseEncoder)
            cause = json.loads(causeJson, object_hook=Generic.from_dict)
            mygoodness_url = 'https://mygoodness.benevity.org/en-ca/cause/' + cause.id
            # result = '*ID:* ' + cause.id + '\n*Location:* ' + cause.attributes.city + ', ' + cause.attributes.state.name
            if "description" in cause_at_idx["attributes"]:
                result = cause.attributes.description + '\n*Location:* ' + cause.attributes.city + ', ' + cause.attributes.state.name
            else:
                result = "Visit MyGoodness for more details!" + '\n*Location:* ' + cause.attributes.city + ', ' + cause.attributes.state.name

            if len(lst_of_causes) > (self.idx+1):
                cause_at_second = lst_of_causes[self.idx+1]
                second_causeJson = json.dumps(cause_at_second, indent=4, cls=CauseEncoder)
                second_cause = json.loads(second_causeJson, object_hook=Generic.from_dict)
                second_url = 'https://mygoodness.benevity.org/en-ca/cause/' + second_cause.id
                second_name = second_cause.attributes.name
                global second_result
                if "description" in cause_at_second['attributes']:
                    second_result = second_cause.attributes.description + '\n*Location:* ' + second_cause.attributes.city + ', ' + second_cause.attributes.state.name
                else:
                    second_result = "Visit MyGoodness for more details!" + '\n*Location:* ' + second_cause.attributes.city + ', ' + second_cause.attributes.state.name
                global second_mygoodness_url
                second_mygoodness_url = second_url
                global second_name_global
                second_name_global = second_name

            else:
                second_url = "https://mygoodness.benevity.org/"
                second_name = "No Results Found"

            if len(lst_of_causes) > (self.idx+2):
                cause_at_third = lst_of_causes[self.idx+2]
                third_causeJson = json.dumps(cause_at_third, indent = 4, cls=CauseEncoder)
                third_cause = json.loads(third_causeJson, object_hook=Generic.from_dict)
                third_url = 'https://mygoodness.benevity.org/en-ca/cause/' + third_cause.id
                third_name = third_cause.attributes.name
                global third_result
                if "description" in cause_at_third['attributes']:
                    third_result = third_cause.attributes.description + '\n*Location:* ' + third_cause.attributes.city + ', ' + third_cause.attributes.state.name
                else:
                    third_result = "Visit MyGoodness for more details!" + '\n*Location:* ' + third_cause.attributes.city + ', ' + third_cause.attributes.state.name
                global third_mygoodness_url
                third_mygoodness_url = third_url
                global third_name_global
                third_name_global = third_name
            else:
                third_url = "https://mygoodness.benevity.org/"
                third_name = "No Results Found"
            respond(
                blocks=[
                    {
                        "type": 'section',
                        "text": {
                            "type": 'mrkdwn',
                            "text": "<" + mygoodness_url + "|*" + cause.attributes.name + "*>\n" + result
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
                                "action_id": "button_click"
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
                ],
                attachments=[
                    {
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "*Alternative Causes*"
                                }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "<" + second_url + "|" + second_name + ">"
                                },
                                "accessory": {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View",
                                    },
                                    "action_id": "view_alternate_1"
                                }
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "<" + third_url + "|" + third_name + ">"
                                },
                                "accessory": {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View",
                                    },
                                    "action_id": "view_alternate_2"
                                }
                            }
                        ]
                    },
                ],
            )
        except:
            respond("No results found.")
            # say("No results found.")