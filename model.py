#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from json import load


class ClientModel:

    def __init__(self, definition_file='oma-object-spec.json', data_file='data.json'):
        with open(definition_file) as file:
            self.definition_dict = load(file)
        with open(data_file) as file:
            self.data_dict = load(file)

        self.validate_data()

    def validate_data(self):
        pass

    def get_objects(self):
        return list(self.data_dict.keys())

    def get_instances(self, object_key):
        return list(self.data_dict[object_key].keys())

    def get_resources(self, object_key, instance_key):
        return list(self.data_dict[object_key][instance_key])

    def get_objects_links(self):
        result = ""
        for obj in self.get_objects():
            for inst in self.get_instances(obj):
                result += "</{}/{}>,".format(obj, inst)

        # remove last ","
        return result[:-1]
