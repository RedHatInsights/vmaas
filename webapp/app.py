#!/usr/bin/python

from tornado.ioloop import IOLoop
import tornado.web
import ujson
import falcon
import errata
import sys
import os

EXAMPLE_MSG = """Example of passing input data as a file: <br />
                 curl -F file=@/path/to/json_file http://hostname:8080/api/v1/json/ <br /> <br />
                 
                 Example of passing imput data as a body of POST request: <br />
                 curl -d "@/path/to/json_file" -H "Content-Type: application/json" -X POST http://hostname:8080/api/v1/json/
                 
              """

cursor = errata.init_db(os.getenv('POSTGRES_DB', errata.DEFAULT_DB_NAME), 
                        os.getenv('POSTGRES_USER', errata.DEFAULT_DB_USER),
                        os.getenv('POSTGRES_PASSWORD', errata.DEFAULT_DB_PASSWORD),
                        os.getenv('POSTGRES_HOST', 'vmaas_db'), 
                        os.getenv('POSTGRES_PORT', errata.DEFAULT_DB_PORT))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(EXAMPLE_MSG)


class PlaintextHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('')

    def post(self):
        plaintext_file = self.request.files['file'][0]['body']
        contents = plaintext_file.split('\n')
        for line in sorted(set(contents)):
            if line and line.strip():
                self.write(str(errata.process(line, cursor)))


class JsonHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('')

    def post(self):
        # extract input JSON from POST request
        json_data = ''
        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        response = {
            'package_list': {},
            'errata_list': {},
            'repo_list': {},
            'nevra_list': {},
            'bugzilla_list': {},
            'cve_list': {}
        }

        # fill response with packages
        try:
            data = ujson.loads(json_data)
            for pkg in sorted(set(data['package_list'])):
                if pkg and pkg.strip():
                    # put empty list of updates for a pkg
                    # and then add real packages if they exist
                    response['package_list'][pkg] = []

                    update_pkgs = errata.process(pkg, cursor)
                    for up_dict in update_pkgs:
                        triple = []

                        pack_name = up_dict['name']
                        if up_dict['epoch'] != '0':
                            pack_name += ':' + up_dict['epoch']
                        pack_name += '-' + up_dict['version'] + '-' + up_dict['release']

                        triple.append(pack_name)
                        triple.append(up_dict['advisory_name'])
                        triple.append(up_dict['repo_name'])

                        response['package_list'][pkg].append(triple)
        except ValueError:
            self.set_status(400, reason='Error: malformed input JSON.')

        # TODO: fill response with errata

        # TODO: fill response with CVEs

        # TODO: fill response with repos

        self.write(ujson.dumps(response))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler),
            (r"/api/v1/plain/?", PlaintextHandler),
            (r"/api/v1/json/?", JsonHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
