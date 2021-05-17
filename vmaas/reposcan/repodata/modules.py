"""
Module containing class for modules metadata.
"""
import yaml


class ModuleMD:
    """Class parsing modules.yaml, takes filename in the constructor"""
    def __init__(self, filename):
        self.modules = []
        module_dict = {}
        default_list = []

        with open(filename, 'r') as fdesc:
            content = fdesc.read()
        groups = content.replace('...', '').split('---')[1:]  # get rid of modulemd separators
        for chunk in groups:
            parsed = yaml.full_load(chunk)
            data = parsed['data']
            if parsed['document'] == 'modulemd':
                name = data['name']
                stream = data['stream']
                if not name in module_dict:
                    module_dict[name] = {}
                if not stream in module_dict[name]:
                    module_dict[name][stream] = []
                new_stream = {}
                new_stream['name'] = name
                new_stream['arch'] = data.get('arch')
                new_stream['version'] = int(data.get('version'))
                new_stream['context'] = str(data.get('context'))
                new_stream['stream'] = str(stream)
                new_stream['profiles'] = data.get('profiles', [])
                for profile_name in new_stream['profiles']:
                    new_stream['profiles'][profile_name]['default_profile'] = False
                if 'artifacts' in data:
                    new_stream['artifacts'] = data.get('artifacts').get('rpms', [])
                new_stream['default_stream'] = False
                module_dict[name][stream].append(new_stream)
            elif parsed['document'] == 'modulemd-defaults':
                default_list.append(parsed)
        self._parse_modulemd_defaults(module_dict, default_list)
        for name in module_dict:
            for stream in module_dict[name]:
                self.modules.extend(module_dict[name][stream])

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

    def list_modules(self):
        """Returns list of parsed modules (list of dictionaries)."""
        return self.modules
