"""
Module containing classes for fetching/importing modules from/into database.
"""

from psycopg2.extras import execute_values

from database.object_store import ObjectStore


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
                for row in cur.fetchall():
                    module_map[(row[1], row[2],)] = row[0]
                    names.remove((row[1], row[2], row[3]))
            if names:
                import_data = set()
                for module in modules:
                    if (module['name'], arch_map[module['arch']], repo_id) in names:
                        import_data.add((module['name'], repo_id, arch_map[module['arch']]))
                execute_values(cur,
                               """insert into module (name, repo_id, arch_id)
                                  values %s returning id, name, arch_id""",
                               list(import_data), page_size=len(import_data))
                for row in cur.fetchall():
                    module_map[(row[1], row[2],)] = row[0]
            for module in modules:
                module['module_id'] = module_map[(module['name'], arch_map[module['arch']],)]
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure putting new module for repo_id %s into db.", repo_id)
            self.conn.rollback()
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
                for row in cur.fetchall():
                    stream_map[(row[1], row[2], row[3], row[4])] = row[0]
                    streams.remove((row[1], row[2], row[3], row[4]))
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
                for row in cur.fetchall():
                    stream_map[(row[1], row[2], row[3], row[4])] = row[0]
            for module in modules:
                module['stream_id'] = stream_map[(module['module_id'], module['stream'],
                                                  module['version'], module['context'])]
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure when inserting into module_stream.")
            self.conn.rollback()
        finally:
            cur.close()
        return modules

    def create_module(self, repo_id, module):
        """Creates a new module stream (used for new module N:S:V:C introduced in errata)"""
        module['default_stream'] = False
        modules = self._populate_modules(repo_id, [module])
        modules = self._populate_streams(modules)
        return modules[0]
