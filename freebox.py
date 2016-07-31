#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json


freebox_config_file = 'freebox.json'


class Freebox:
    uid = None
    api_base_url = None
    device_type = None
    app_token = None
    ip = None

    session_challenge = None
    session_token = None

    def __init(self, uid, api_base_url, device_type):
        self.uid = uid
        self.api_base_url = api_base_url
        self.device_type = device_type

    @staticmethod
    def get_api_call_uri():
        return 'http://mafreebox.freebox.fr/api/v3/'

    def save(self):
        with open(freebox_config_file, 'w') as output:
            json.dump(self.__dict__, output)

    @staticmethod
    def retrieve():
        freebox = Freebox()
        with open(freebox_config_file, 'r') as input:
            freebox.__dict__ = json.load(input)

        return freebox


def get_freebox():
    return Freebox.retrieve()
