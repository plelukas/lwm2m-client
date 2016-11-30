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
    """
    if resource has one instance and read is only for that resource the format is:
        {"e": [
            {"n": "", "v": <value>}
        ]}
    if resource has many instances:
        if read is from single resource the format is:
        {"e": [
            {"n": "<sub_resource>", "v": <value>},
            {"n": "<sub_resource>", "v": <value>},
            ...
        ]}

        if read is from object instance the format is:
        {"e": [
            {"n": "<resource>/<sub_resource>", "v": <value>},
            {"n": "<resource>/<sub_resource>", "v": <value>},
            ...
        ]}
    """

    def __init__(self, model):
        self.model = model

    def make_response_dict(self):
        return {"e": []}

    def get_resource_dict(self, resource_path, value, sub_resource=None, is_single_read=False):
        """

        :param resource_path:
        :param value:
        :param sub_resource: used when resource has many instances (ex. power sources)
        :param is_single_read: used when read is performed only on that resource

        :return: python dict ready to json dump
        """
        result = {}
        if is_single_read and sub_resource is None:
            result["n"] = ""
        else:
            if sub_resource is None:
                if is_single_read:
                    result["n"] = ""
                else:
                    result["n"] = str(resource_path[2])
            else:
                if not is_single_read:
                    result["n"] = str(resource_path[2]) + "/{}".format(sub_resource)
                else:
                    result["n"] = str(sub_resource)
        # simply map types from definition_dict "type" based on TYPES_MAP
        result[TYPES_MAP[self.model.get_definition_resource(resource_path)["type"]]] = value
        return result

    def encode_read_resource(self, resource_path):
        result_value = self.model.handle_resource_read(resource_path)
        result = self.make_response_dict()
        if isinstance(result_value, dict):
            for k, v in result_value.items():
                resource_dict = self.get_resource_dict(resource_path, v, k, is_single_read=True)
                result["e"].append(resource_dict)
        else:
            resource_dict = self.get_resource_dict(resource_path, result_value, is_single_read=True)
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

    def _write_resource(self, resource_path, arg_dict):
        # skip the "n" argument
        for k, v in arg_dict.items():
            if k == "n":
                continue
            arg = v
        return self.model.handle_resource_write(resource_path, arg)

    def encode_write(self, path, payload):
        args_list = loads(payload.decode())['e']
        if len(args_list) > 1:
            result = True
            for arg_dict in args_list:
                resource = arg_dict['n']
                resource_path = path + (resource,)
                result = result and self._write_resource(resource_path, arg_dict)
            return result
        else:
            arg_dict = args_list[0]
            return self._write_resource(path, arg_dict)

