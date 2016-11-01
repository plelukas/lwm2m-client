#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json import loads, dumps


TYPES_MAP = {
    "string": "sv",
    "integer": "v",
    "boolean": "bv",
    "opaque": "sv",
    "time": "v",
    "float": "v"
}


class JSONEncoder:

    def __init__(self, model):
        self.model = model

    def make_response_dict(self):
        return {"e": []}

    def get_resource_dict(self, resource_path, value, sub_resource=None):
        result = {}
        if sub_resource is None:
            result["n"] = str(resource_path[2])
        else:
            result["n"] = str(resource_path[2]) + "/{}".format(sub_resource)
        # simply map types from definition_dict "type" based on TYPES_MAP
        result[TYPES_MAP[self.model.get_definition_resource(resource_path)["type"]]] = value
        return result

    def encode_read_resource(self, resource_path):
        result_value = self.model.handle_resource_read(resource_path)
        result = self.make_response_dict()
        if isinstance(result_value, dict):
            for k, v in result_value.items():
                resource_dict = self.get_resource_dict(resource_path, v, k)
                result["e"].append(resource_dict)
        else:
            resource_dict = self.get_resource_dict(resource_path, result_value)
            result["e"].append(resource_dict)
        return dumps(result).encode()

    def encode_read_instance(self, instance_path):
        result = self.make_response_dict()
        for res in self.model.get_resources(instance_path[0], instance_path[1]):
            resource_path = (instance_path[0], instance_path[1], res)
            if not self.model.is_resource_readable(int(instance_path[0]), int(res)):
                continue
            result_value = self.model.handle_resource_read(resource_path)
            if isinstance(result_value, dict):
                for k, v in result_value.items():
                    resource_dict = self.get_resource_dict(resource_path, v, k)
                    result["e"].append(resource_dict)
            else:
                resource_dict = self.get_resource_dict(resource_path, result_value)
                result["e"].append(resource_dict)
        return dumps(result).encode()


