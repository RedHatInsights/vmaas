"""
Module containing classes for fetching/importing modules from/into database.
"""

import re

from psycopg2.extras import execute_values

from database.object_store import ObjectStore

class ModulesStore(ObjectStore):
    """Class providing interface for storing modules and related info."""

    def __init__(self):
        super().__init__()
        self.nevra_re = re.compile(r'(.*)-(([0-9]+):)?([^-]+)-([^-]+)\.([a-z0-9_]+)')

    def _split_packagename(self, filename):
        """Split rpm name (incl. epoch) to NEVRA components."""
        if filename[-4:] == '.rpm':
            filename = filename[:-4]

        match = self.nevra_re.match(filename)
        if not match:
            return '', '', '', '', ''

        name, _, epoch, version, release, arch = match.groups()
        if epoch is None:
            epoch = '0'
        return name, epoch, version, release, arch

    def _populate_modules(self, repo_id, modules):
        cur = self.conn.cursor()
        names = set()
        module_map = {}
        arch_map = self._prepare_arch_map()
        for module in modules:
            names.add((module['name'], arch_map[module['arch']],))
        if names:
            execute_values(cur,
                           """select id, name, arch_id from module
                              inner join (values %s) t(name, arch_id)
                              using (name, arch_id)
                           """, list(names), page_size=len(names))
            for row in cur.fetchall():
                module_map[(row[1], row[2],)] = row[0]
                names.remove((row[1], row[2],))
        if names:
            import_data = set()
            for module in modules:
                if (module['name'], arch_map[module['arch']],) in names:
                    import_data.add((module['name'], repo_id, arch_map[module['arch']]))
            execute_values(cur,
                           """insert into module (name, repo_id, arch_id)
                            values %s returning id, name, arch_id""",
                           list(import_data), page_size=len(import_data))
            for row in cur.fetchall():
                module_map[(row[1], row[2],)] = row[0]
        cur.close()
        self.conn.commit()
        for module in modules:
            module['module_id'] = module_map[(module['name'], arch_map[module['arch']],)]
        return modules

    def _populate_streams(self, modules):
        cur = self.conn.cursor()
        streams = set()
        stream_map = {}
        for module in modules:
            streams.add((module['module_id'], module['stream'],))
        if streams:
            execute_values(cur,
                           """select id, module_id, stream_name from module_stream
                              inner join (values %s) t(module_id, stream_name)
                              using (module_id, stream_name)
                           """, list(streams), page_size=len(streams))
            for row in cur.fetchall():
                stream_map[(row[1], row[2],)] = row[0]
                streams.remove((row[1], row[2],))
        if streams:
            import_data = set()
            for module in modules:
                if (module['module_id'], module['stream'],) in streams:
                    import_data.add((module['module_id'], module['stream'], module['default_stream']))
            execute_values(cur,
                           """insert into module_stream (module_id, stream_name, is_default)
                              values %s returning id, module_id, stream_name""",
                           list(import_data), page_size=len(import_data))
            for row in cur.fetchall():
                stream_map[(row[1], row[2],)] = row[0]
        for module in modules:
            module['stream_id'] = stream_map[(module['module_id'], module['stream'])]
        cur.close()
        self.conn.commit()
        return modules

    def _populate_rpm_artifacts(self, modules, repo_id):
        cur = self.conn.cursor()
        nevras_in_repo = self._get_nevras_in_repo(repo_id)
        to_associate = set()
        for module in modules:
            for rpm in module['artifacts']:
                to_associate.add((nevras_in_repo[self._split_packagename(rpm)], module['stream_id'],))
        if to_associate:
            execute_values(cur,
                           """select pkg_id, stream_id from module_rpm_artifact
                               inner join (values %s) t(pkg_id, stream_id)
                               using (pkg_id, stream_id)
                           """, list(to_associate), page_size=len(to_associate))
            for row in cur.fetchall():
                to_associate.remove((row[0], row[1],))
        if to_associate:
            execute_values(cur,
                           """insert into module_rpm_artifact (pkg_id, stream_id)
                              values %s""",
                           list(to_associate), page_size=len(to_associate))
        cur.close()
        self.conn.commit()

    def _populate_profiles(self, modules):
        cur = self.conn.cursor()
        profiles = set()
        profile_map = {}
        for module in modules:
            for profile in module['profiles']:
                profiles.add((module['stream_id'], profile,))
        if profiles:
            execute_values(cur,
                           """select id, stream_id, profile_name from module_profile
                              inner join (values %s) t(stream_id, profile_name)
                              using (stream_id, profile_name)
                           """, list(profiles), page_size=len(profiles))
            for row in cur.fetchall():
                profile_map[(row[1], row[2],)] = row[0]
                profiles.remove((row[1], row[2],))
        if profiles:
            import_data = set()
            for module in modules:
                for profile in module['profiles']:
                    if (module['stream_id'], profile,) in profiles:
                        import_data.add(
                            (module['stream_id'], profile, module['profiles'][profile]['default_profile'],))
            execute_values(cur,
                           """insert into module_profile (stream_id, profile_name, is_default)
                              values %s returning id, stream_id, profile_name""",
                           list(import_data), page_size=len(import_data))
            for row in cur.fetchall():
                profile_map[(row[1], row[2],)] = row[0]
        for module in modules:
            for profile in module['profiles']:
                module['profiles'][profile]['profile_id'] = profile_map[(module['stream_id'], profile,)]
        cur.close()
        self.conn.commit()
        return modules

    def _populate_profile_names(self, modules):
        cur = self.conn.cursor()
        package_name_map = self._prepare_package_name_map()
        to_associate = set()
        for module in modules:
            for profile in module['profiles']:
                profile_id = module['profiles'][profile]['profile_id']
                for rpm_name in module['profiles'][profile]['rpms']:
                    try:
                        to_associate.add((package_name_map[rpm_name], profile_id,))
                    except KeyError:
                        # TODO: this whole try/except block is there due to poor modularity design
                        # TODO: to actually fix this we would need to implement parsing and storing
                        # TODO: of package provides
                        execute_values(cur,
                                       """insert into package_name (name)
                                          values %s returning id""",
                                       [(rpm_name,)], page_size=1)
                        name_id = cur.fetchall()[0][0]
                        to_associate.add((name_id, profile_id),)
                        package_name_map[rpm_name] = name_id
        if to_associate:
            execute_values(cur,
                           """select package_name_id, profile_id from module_profile_pkg
                              inner join (values %s) t(package_name_id, profile_id)
                              using (package_name_id, profile_id)
                           """, list(to_associate), page_size=len(to_associate))
            for row in cur.fetchall():
                to_associate.remove((row[0], row[1],))
        if to_associate:
            execute_values(cur,
                           """insert into module_profile_pkg (package_name_id, profile_id)
                              values %s""",
                           list(to_associate), page_size=len(to_associate))
        cur.close()
        self.conn.commit()

    def store(self, repo_id, modules):
        """Import all modules from repository into all related DB tables."""

        modules = self._populate_modules(repo_id, modules)
        modules = self._populate_streams(modules)
        self._populate_rpm_artifacts(modules, repo_id)
        modules = self._populate_profiles(modules)
        self._populate_profile_names(modules)
