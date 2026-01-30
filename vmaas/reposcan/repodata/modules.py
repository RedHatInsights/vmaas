"""
Module containing class for modules metadata.
"""
import yaml


class StreamStringPreservingLoader(yaml.FullLoader):  # pylint: disable=too-many-ancestors
    """Customized class to load module stream floats in source yaml as strings."""

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)

            # If key is 'stream' and value is tagged as float
            if key == 'stream' and value_node.tag == 'tag:yaml.org,2002:float':
                value = value_node.value  # Preserve float as string
            # If the value is list of floats
            # (handles module required streams, possibly other lists but shouldn't matter)
            elif value_node.tag == 'tag:yaml.org,2002:seq':
                value = []
                for item_node in value_node.value:
                    if item_node.tag == 'tag:yaml.org,2002:float':
                        value.append(item_node.value)  # Preserve float as string
                    else:
                        value.append(self.construct_object(item_node, deep=deep))
            else:
                value = self.construct_object(value_node, deep=deep)

            mapping[key] = value
        return mapping


class ModuleMD:
    """Class parsing modules.yaml, takes filename in the constructor"""

    def __init__(self, filename):
        self.modules = []
        module_dict = {}
        default_list = []

        with open(filename, 'r', encoding='utf8') as fdesc:
            content = fdesc.read()
        groups = content.replace('...', '').split('---')[1:]  # get rid of modulemd separators
        for chunk in groups:
            parsed = yaml.load(chunk, Loader=StreamStringPreservingLoader)
            data = parsed['data']
            if parsed['document'] == 'modulemd':
                name = data['name']
                stream = str(data['stream'])
                if name not in module_dict:
                    module_dict[name] = {}
                if stream not in module_dict[name]:
                    module_dict[name][stream] = []
                new_stream = {}
                new_stream['name'] = name
                new_stream['arch'] = data.get('arch')
                new_stream['version'] = int(data.get('version'))
                new_stream['context'] = str(data.get('context'))
                new_stream['stream'] = stream
                new_stream['profiles'] = data.get('profiles', [])
                for profile_name in new_stream['profiles']:
                    new_stream['profiles'][profile_name]['default_profile'] = False
                if 'artifacts' in data:
                    new_stream['artifacts'] = data.get('artifacts').get('rpms', [])
                new_stream['default_stream'] = False
                if 'dependencies' in data and 'requires' in data['dependencies'][0]:
                    new_stream['requires'] = self._parse_requires(data['dependencies'][0]['requires'])
                module_dict[name][stream].append(new_stream)
            elif parsed['document'] == 'modulemd-defaults':
                default_list.append(parsed)
        self._parse_modulemd_defaults(module_dict, default_list)
        for mod in module_dict.values():
            for stream in mod:
                self.modules.extend(mod[stream])

    @staticmethod
    def _parse_modulemd_defaults(module_dict, default_list):
        for parsed in default_list:
            data = parsed['data']
            name = data.get('module')
            default_stream = data.get('stream')
            if default_stream and default_stream in module_dict[name]:
                for stream_dict in module_dict[name][default_stream]:
                    stream_dict['default_stream'] = True
            for stream in data['profiles']:
                if stream not in module_dict[name]:
                    continue  # this is here due to module defaults referencing non-existing modules
                default_profile = data['profiles'][stream]
                if default_profile:
                    for stream_dict in module_dict[name][stream]:
                        if default_profile[0] and default_profile[0] in stream_dict['profiles']:
                            stream_dict['profiles'][default_profile[0]]['default_profile'] = True

    @staticmethod
    def _parse_requires(requires_in):
        requires = {}
        for req_mod, req_streams in requires_in.items():
            # platform requirement is not module
            if req_mod == "platform":
                continue
            requires[req_mod] = [str(req_stream) for req_stream in req_streams]
        return requires

    def list_modules(self):
        """Returns list of parsed modules (list of dictionaries)."""
        return self.modules
