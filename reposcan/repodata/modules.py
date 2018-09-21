"""
Module containing class for modules metadata.
"""
import yaml

class ModuleMD(object):
    """Class parsing modules.yaml, takes filename in the constructor"""
    def __init__(self, filename):
        self.modules = []
        module_dict = {}

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
                module_dict[name][stream]['stream'] = str(stream)
                module_dict[name][stream]['profiles'] = data.get('profiles', [])
                for profile_name in module_dict[name][stream]['profiles']:
                    module_dict[name][stream]['profiles'][profile_name]['default_profile'] = False
                module_dict[name][stream]['artifacts'] = data.get('artifacts').get('rpms', [])
                module_dict[name][stream]['default_stream'] = False
            elif parsed['document'] == 'modulemd-defaults':
                name = data.get('module')
                default_stream = data.get('stream', None)
                if default_stream:
                    module_dict[name][default_stream]['default_stream'] = True
                for stream in data['profiles']:
                    default_profile = data['profiles'][stream]
                    if default_profile:
                        module_dict[name][stream]['profiles'][default_profile[0]]['default_profile'] = True
        for name in module_dict:
            for stream in module_dict[name]:
                self.modules.append(module_dict[name][stream])

    def list_modules(self):
        """Returns list of parsed modules (list of dictionaries)."""
        return self.modules
