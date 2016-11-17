#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import copy
from json import load

import handlers


class ClientModel:

    def __init__(self, definition_file='oma-objects-spec.json', data_file='data.json'):
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
        return list(self.data_dict[object_key][instance_key].keys())

    def is_resource_readable(self, object_num, resource_num):
        return 'R' in self.definition_dict[object_num]["resourcedefs"][resource_num]["operations"]

    def is_resource_writable(self, object_num, resource_num):
        return 'W' in self.definition_dict[object_num]["resourcedefs"][resource_num]["operations"]

    def is_resource_executable(self, object_num, resource_num):
        return 'E' in self.definition_dict[object_num]["resourcedefs"][resource_num]["operations"]

    def get_instances_iter_paths(self):
        for obj in self.get_objects():
            for inst in self.get_instances(obj):
                yield (obj, inst)

    def get_resources_iter_paths(self):
        for obj in self.get_objects():
            for inst in self.get_instances(obj):
                for res in self.get_resources(obj, inst):
                    yield (obj, inst, res)

    def get_objects_links(self):
        result = ""
        for obj in self.get_objects():
            for inst in self.get_instances(obj):
                result += "</{}/{}>,".format(obj, inst)

        # remove last ","
        return result[:-1]

    def get_definition_resource(self, resource_path):
        return self.definition_dict[int(resource_path[0])]["resourcedefs"][int(resource_path[2])]

    def handle_read(self, val_or_func):
        if not isinstance(val_or_func, str):
            if isinstance(val_or_func, dict):
                result = copy.deepcopy(val_or_func)
                for k, v in result.items():
                    result[k] = self.handle_read(v)
                return result
            return val_or_func
        if hasattr(handlers, val_or_func):
            return getattr(handlers, val_or_func)()
        return val_or_func

    def handle_resource_read(self, resource_path):
        val_or_func = self.data_dict[resource_path[0]][resource_path[1]][resource_path[2]]
        return self.handle_read(val_or_func)

    def handle_resource_exec(self, resource_path, params_list):
        func_name = self.data_dict[resource_path[0]][resource_path[1]][resource_path[2]]
        if isinstance(func_name, str) and hasattr(handlers, func_name):
            getattr(handlers, func_name)(params_list)
            return True
        return False

    def is_function(self, val_or_func):
        if isinstance(val_or_func, str):
            if hasattr(handlers, val_or_func):
                return True
        return False

    def handle_resource_write(self, resource_path, arg):
        val_or_func = self.data_dict[resource_path[0]][resource_path[1]][resource_path[2]]
        if self.is_function(val_or_func):
            return getattr(handlers, val_or_func)(arg)
        else:
            self.data_dict[resource_path[0]][resource_path[1]][resource_path[2]] = arg
            return True
