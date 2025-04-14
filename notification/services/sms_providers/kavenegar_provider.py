import json

import requests
from django.conf import settings
from kavenegar import APIException, HTTPException, KavenegarAPI

from notification.services.sms_providers.base_sms_provider import BaseSMSProvider


class APIException(Exception):
    pass


class HTTPException(Exception):
    pass


class KavenegarAPI(object):
    def __init__(self, apikey):
        self.version = "v1"
        self.host = "api.kavenegar.com"
        self.apikey = apikey
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "utf-8",
        }

    def __repr__(self):
        return "kavenegar.KavenegarAPI({!r})".format(self.apikey)

    def __str__(self):
        return "kavenegar.KavenegarAPI({!s})".format(self.apikey)

    def _request(self, action, method, params={}):
        url = (
            "https://"
            + self.host
            + "/"
            + self.version
            + "/"
            + self.apikey
            + "/"
            + action
            + "/"
            + method
            + ".json"
        )
        try:
            content = requests.post(
                url, headers=self.headers, auth=None, data=params
            ).content
            try:
                response = json.loads(content.decode("utf-8"))
                if response["return"]["status"] == 200:
                    response = response["entries"]
                else:
                    raise APIException(
                        (
                            "APIException[%s] %s"
                            % (
                                response["return"]["status"],
                                response["return"]["message"],
                            )
                        ).encode("utf-8")
                    )
            except ValueError as e:
                raise HTTPException(e)
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPException(e)

    def sms_send(self, params=None):
        return self._request("sms", "send", params)

    def sms_sendarray(self, params=None):
        return self._request("sms", "sendarray", params)

    def sms_status(self, params=None):
        return self._request("sms", "status", params)

    def sms_statuslocalmessageid(self, params=None):
        return self._request("sms", "statuslocalmessageid", params)

    def sms_select(self, params=None):
        return self._request("sms", "select", params)

    def sms_selectoutbox(self, params=None):
        return self._request("sms", "selectoutbox", params)

    def sms_latestoutbox(self, params=None):
        return self._request("sms", "latestoutbox", params)

    def sms_countoutbox(self, params=None):
        return self._request("sms", "countoutbox", params)

    def sms_cancel(self, params=None):
        return self._request("sms", "cancel", params)

    def sms_receive(self, params=None):
        return self._request("sms", "receive", params)

    def sms_countinbox(self, params=None):
        return self._request("sms", "countinbox", params)

    def sms_countpostalcode(self, params=None):
        return self._request("sms", "countpostalcode", params)

    def sms_sendbypostalcode(self, params=None):
        return self._request("sms", "sendbypostalcode", params)

    def verify_lookup(self, params=None):
        return self._request("verify", "lookup", params)

    def call_maketts(self, params=None):
        return self._request("call", "maketts", params)

    def call_status(self, params=None):
        return self._request("call", "status", params)

    def account_info(self):
        return self._request("account", "info")

    def account_config(self, params=None):
        return self._request("account", "config", params)


class KavenegarSMSProvider(BaseSMSProvider):
    """
    SMS provider using Kavenegar API.
    """

    def __init__(self):
        """
        Initializes the Kavenegar API instance.
        """
        self.api_key = settings.SMS_SERVER_API_KEY
        self.sender_number = settings.SMS_NUMBER_SENDER

    def send_sms(self, recipient: str, message: str) -> bool:
        """
        Send an SMS via Kavenegar.

        :param recipient: The recipient's phone number.
        :param message: The SMS content.
        :return: True if sent successfully, False otherwise.
        """
        try:
            api = KavenegarAPI(self.api_key)
            params = {
                "sender": self.sender_number,
                "receptor": recipient,
                "message": message,
            }
            api.sms_send(params)
            print(f"SMS sent successfully to {recipient}")
            return True

        except (APIException, HTTPException) as e:
            print(f"Failed to send SMS: {e}")
            return False
