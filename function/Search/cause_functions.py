import json
import http.client
import logging
import requests
from json import JSONEncoder, JSONDecodeError

# for lambda function
from function.Search import CAUSE_SEARCH_API, AUTH_URL, AUTH_TOKEN, MYGOODNESS_URL
from function.Search.cause_search_result_dto import CauseSearchResultDto

class SearchCause:
    def __init__(self, text):
        self.text = text
        # self.test_url = None

    def return_cause(self, text):
        """
        Transforms the search-cause response into a list of causes in json format and returns the result
        :param text: describes the cause being searched by the user
        :return: returns an array of causes in json format
        """
        logging.info("The search command received: {}".format(text))
        conn = http.client.HTTPSConnection(CAUSE_SEARCH_API)
        auth_token = self.get_auth_token()
        payload = ''
        headers = {
            'Accept-Encoding': 'utf-8',
            'Authorization': auth_token
        }
        search_url = "/search/causes?q=" + "%22" + text + "%22"
        logging.info("Search URL is: {}".format(search_url))
        conn.request("GET", search_url, payload, headers)
        res = conn.getresponse()
        data = res.read()

        rdata = data.decode("utf-8")
        rdata = json.loads(rdata)
        rdata = rdata["data"]
        return rdata

    def get_auth_token(self):
        """ Generates the authorization bearer test token for return_cause method """
        url = AUTH_URL
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': AUTH_TOKEN}
        try:
            response = requests.post(url, headers=headers)
            auth_json = response.content
            auth_data = json.loads(auth_json)
            return auth_data['access_token']
        except (ConnectionError, JSONDecodeError, KeyError) as ex:
            logging.error('Exception occurred while getting the auth token')
            logging.error(ex)

class CauseEncoder(JSONEncoder):
    def default(self, o):
        """
        Encodes instances of a data type as JSON objects
        :param o:
        :return:
        """
        return o.__dict__

class Generic:
    @classmethod
    def from_dict(cls, dict):
        """

        :param dict:
        :return:
        """
        obj = cls()
        obj.__dict__.update(dict)
        return obj

class CauseHelper:
    def __init__(self, edited_command, idx):
        self.edited_command = edited_command
        self.idx = idx
        self.list_of_causes = None

    def get_list_of_causes(self, edited_command):
        """
        Returns a list of causes
        :param edited_command: Describes the list of causes
        :return: returns a list of causes
        """
        # get list of causes in json format
        search_cause = SearchCause(edited_command)
        lst_of_causes = search_cause.return_cause(edited_command)

        return lst_of_causes

    def search_cause(self, lst_of_causes, idx):
        """
        Description: Creates and returns a DTO containing the information of the cause searched
        :param lst_of_causes: a list of causes
        :return: returns a DTO with information on the cause being searched
        """

        cause_search_dto = CauseSearchResultDto()
        if len(lst_of_causes) < 1:
            return cause_search_dto

        # get cause at i = idx
        cause_at_idx = lst_of_causes[idx]
        # converting to JSON string
        causeJson = json.dumps(cause_at_idx, indent=4, cls=CauseEncoder)
        # converting to JSON object
        cause = json.loads(causeJson, object_hook=Generic.from_dict)

        # link to mygoodness for primary cause
        cause_search_dto.mygoodness_url = MYGOODNESS_URL + cause.id
        cause_search_dto.first_name_global = cause.attributes.name
        if "description" in cause_at_idx["attributes"]:
            cause_search_dto.description = cause.attributes.description
        else:
            cause_search_dto.description = "Visit MyGoodness for more details!"

        cause_search_dto.location = '\n*Location:* ' + cause.attributes.city + ', ' + cause.attributes.state.name
        if "logo" in cause_at_idx["attributes"]:
            cause_search_dto.logo = cause.attributes.logo
        else:
            cause_search_dto.logo = "https://back.3blmedia.com/sites/default/files/Clients/Benevity_NewSite_Tile.png"

        return cause_search_dto

