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
            parsed = yaml.load(chunk)
            data = parsed['data']
            if parsed['document'] == 'modulemd':
                name = data['name']
                stream = data['stream']
                if not name in module_dict:
                    module_dict[name] = {}
                module_dict[name][stream] = {}
                module_dict[name][stream]['name'] = name
                module_dict[name][stream]['arch'] = data.get('arch')
                module_dict[name][stream]['version'] = int(data.get('version'))
                module_dict[name][stream]['context'] = str(data.get('context'))
                module_dict[name][stream]['stream'] = str(stream)
                module_dict[name][stream]['profiles'] = data.get('profiles', [])
                for profile_name in module_dict[name][stream]['profiles']:
                    module_dict[name][stream]['profiles'][profile_name]['default_profile'] = False
                if 'artifacts' in module_dict[name][stream]:
                    module_dict[name][stream]['artifacts'] = data.get('artifacts').get('rpms', [])
                module_dict[name][stream]['default_stream'] = False
            elif parsed['document'] == 'modulemd-defaults':
                default_list.append(parsed)
        self._parse_modulemd_defaults(module_dict, default_list)
        for name in module_dict:
            for stream in module_dict[name]:
                self.modules.append(module_dict[name][stream])

    @staticmethod
    def _parse_modulemd_defaults(module_dict, default_list):
        for parsed in default_list:
            data = parsed['data']
            name = data.get('module')
            default_stream = data.get('stream', None)
            if default_stream:
                module_dict[name][default_stream]['default_stream'] = True
            for stream in data['profiles']:
                if stream not in module_dict[name]:
                    continue # this is here due to module defaults referencing non-existing modules
                default_profile = data['profiles'][stream]
                if default_profile and default_profile[0] in module_dict[name][stream]['profiles']:
                    module_dict[name][stream]['profiles'][default_profile[0]]['default_profile'] = True

    def list_modules(self):
        """Returns list of parsed modules (list of dictionaries)."""
        return self.modules
