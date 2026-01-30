"""
Module containing classes for fetching/importing modules from/into database.
"""

from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.common import rpm_utils


class ModulesStore(ObjectStore):
    """Class providing interface for storing modules and related info."""

    def _populate_modules(self, repo_id, modules):
        cur = self.conn.cursor()
        try:
            names = set()
            module_map = {}
            arch_map = self._prepare_table_map(["name"], "arch")
            for module in modules:
                names.add((module['name'], arch_map[module['arch']], repo_id))
            if names:
                execute_values(cur,
                               """select id, name, arch_id, repo_id from module
                                  inner join (values %s) t(name, arch_id, repo_id)
                                  using (name, arch_id, repo_id)
                               """, list(names), page_size=len(names))
                for r_id, r_name, r_arch_id, r_repo_id in cur.fetchall():
                    module_map[(r_name, r_arch_id,)] = r_id
                    names.remove((r_name, r_arch_id, r_repo_id))
            if names:
                import_data = set()
                for module in modules:
                    if (module['name'], arch_map[module['arch']], repo_id) in names:
                        import_data.add((module['name'], repo_id, arch_map[module['arch']]))
                execute_values(cur,
                               """insert into module (name, repo_id, arch_id)
                                  values %s returning id, name, arch_id""",
                               list(import_data), page_size=len(import_data))
                for r_id, r_name, r_arch_id in cur.fetchall():
                    module_map[(r_name, r_arch_id,)] = r_id
            for module in modules:
                module['module_id'] = module_map[(module['name'], arch_map[module['arch']],)]
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure putting new module for repo_id %s into db.", repo_id)
            self.conn.rollback()
            raise
        finally:
            cur.close()
        return modules

    def _populate_streams(self, modules):
        cur = self.conn.cursor()
        try:
            streams = set()
            stream_map = {}
            for module in modules:
                streams.add((module['module_id'], module['stream'], module['version'], module['context'],))
            if streams:
                execute_values(cur,
                               """select id, module_id, stream_name, version, context from module_stream
                                  inner join (values %s) t(module_id, stream_name, version, context)
                                  using (module_id, stream_name, version, context)
                               """, list(streams), page_size=len(streams))
                for r_id, r_module_id, r_stream_name, r_version, r_context in cur.fetchall():
                    stream_map[(r_module_id, r_stream_name, r_version, r_context)] = r_id
                    streams.remove((r_module_id, r_stream_name, r_version, r_context))
            if streams:
                import_data = set()
                for module in modules:
                    if (module['module_id'], module['stream'], module['version'], module['context']) in streams:
                        import_data.add((module['module_id'], module['stream'], module['version'], module['context'],
                                         module['default_stream']))
                execute_values(cur,
                               """insert into module_stream (module_id, stream_name, version, context, is_default)
                                  values %s returning id, module_id, stream_name, version, context""",
                               list(import_data), page_size=len(import_data))
                for r_id, r_module_id, r_stream_name, r_version, r_context in cur.fetchall():
                    stream_map[(r_module_id, r_stream_name, r_version, r_context)] = r_id
            for module in modules:
                module['stream_id'] = stream_map[(module['module_id'], module['stream'],
                                                  module['version'], module['context'])]
            self.conn.commit()
            return modules
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure when inserting into module_stream.")
            self.conn.rollback()
            raise
        finally:
            cur.close()

    @staticmethod
    def _module_stream_requires(module):
        requires = set()
        if 'requires' in module:
            for req_mod, req_streams in module['requires'].items():
                for req_stream in req_streams:
                    requires.add((req_mod, req_stream))
        return requires

    def _populate_stream_requires(self, modules):
        cur = self.conn.cursor()
        try:
            stream_map = {}
            for module in modules:
                stream_map[(module['name'], module['stream'])] = module['stream_id']

            stream_requires = set()
            for module in modules:
                for req in self._module_stream_requires(module):
                    req_id = stream_map.get(req)
                    if req_id:
                        stream_requires.add((module['stream_id'], req_id))
                    else:
                        self.logger.warning("Unable to map module: %s", req)
            if stream_requires:
                execute_values(cur,
                               """insert into module_stream_require (module_stream_id, require_id)
                                  values %s on conflict (module_stream_id, require_id) do nothing""",
                               list(stream_requires), page_size=len(stream_requires))
            self.conn.commit()
            return modules
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure when inserting into module_stream.")
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def _populate_rpm_artifacts(self, modules, repo_id):
        cur = self.conn.cursor()
        try:  # pylint: disable=too-many-nested-blocks
            nevras_in_repo = self._get_nevras_in_repo(repo_id)
            to_associate = set()
            for module in modules:
                if 'artifacts' in module:
                    for artifact in module['artifacts']:
                        split_pkg_name = rpm_utils.parse_rpm_name(artifact, default_epoch='0',
                                                                  raise_exception=True)
                        if split_pkg_name in nevras_in_repo:
                            to_associate.add((nevras_in_repo[split_pkg_name], module['stream_id'],))
                        else:
                            self.logger.debug('Nevra %s missing in repo %s', artifact, repo_id)
            if to_associate:
                execute_values(cur,
                               """select pkg_id, stream_id from module_rpm_artifact
                                   inner join (values %s) t(pkg_id, stream_id)
                                   using (pkg_id, stream_id)
                               """, list(to_associate), page_size=len(to_associate))
                for r_pkg_id, r_stream_id in cur.fetchall():
                    to_associate.remove((r_pkg_id, r_stream_id,))
            if to_associate:
                execute_values(cur,
                               """insert into module_rpm_artifact (pkg_id, stream_id)
                                  values %s""",
                               list(to_associate), page_size=len(to_associate))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure while populating rpm artifacts")
            self.conn.rollback()
        finally:
            cur.close()

    def create_module(self, repo_id, module):
        """Creates a new module stream (used for new module N:S:V:C introduced in errata)"""
        # if some steps below fail, invalid data may carry on to the next
        # step.  Specifically _populate_modules and _populate_streams
        # could return modules with invalid/incomplete data.
        try:
            module['default_stream'] = False
            modules = self._populate_modules(repo_id, [module])
            modules = self._populate_streams(modules)
            modules = self._populate_stream_requires(modules)
            return modules[0]
        except Exception:  # pylint: disable=broad-except
            # exception already logged.
            return {}

    def store(self, repo_id, modules):
        """Import all modules from repository into all related DB tables."""
        # if some steps below fail, invalid data may carry on to the next
        # step.  Specifically _populate_modules and _populate_streams
        # could return modules with invalid/incomplete data.
        try:
            if modules:
                modules = self._populate_modules(repo_id, modules)
                modules = self._populate_streams(modules)
                modules = self._populate_stream_requires(modules)
                self._populate_rpm_artifacts(modules, repo_id)
        except Exception:  # pylint: disable=broad-except
            # exception already logged.
            pass
