
```py
import requests
import argparse
import json as JSON
import 
from commanded import with_commands, command, command_arg

gist_id_arg = command_arg('gist', nargs=1, type=str,
    help='ID of the gist to delete (e.g: aa5a315d61ae9438b18d)'
)
json_arg = command_arg('--json', help='Outputs the result as raw json',
    action='store_true')

@with_commands(description="Use gist api with a CLI.")
class GistApi:
    API_URL = "https://api.github.com"
    token = env.ACCESS_TOKEN

    def scope_params(self): return { 'scope': 'gist' }

    def auth_header(self): return { 'Authorization': "token %s" % self.token }

    def as_json(self, obj): return JSON.dumps(obj, indent=4)

    @command(name='show', help='Show details of a gist',args=(gist_id_arg,))
    def show(self, gist):
        url = "{base}/gists/{id}".format(base=self.API_URL, id=gist[0])
        req = requests.get(url, params=self.scope_params(),
            headers=self.auth_header())
        print(self.as_json(req.json()))

    @command(name='delete', help='Delete a gist', args=(gist_id_arg,))
    def delete(self, gist):
        id = gist[0]
        url = "{base}/gists/{id}".format(base=self.API_URL, id=id)
        req = requests.delete(url, params=self.scope_params(),
            headers=self.auth_header())

        deleted = req.status_code == 204
        print(
            ("Deleted gist %s" if deleted else  "An error occured with gist %s") % id
        )

    @command(name='list', help='List your gist', args=(json_arg,))
    def list(self, json=False):
        url = '%s/gists' % self.API_URL
        req = requests.get(url,
            params=self.scope_params(),
            headers=self.auth_header())

        data = req.json()
        if json:
            print(self.as_json(data))
        else:
            print("Retrieved %s gist:" % len(data))
            print("\n".join(list(
                map(lambda gist: "  %s" % "\t".join([
                    "id: %s" % gist['id'],
                    "url: %s" % gist['html_url'],
                    "created: %s" % gist['created_at'],
                    "nb files: %s" % len(gist['files'].keys()),
                    gist['description']
                ]), data)
            )))

    @command(
        name='create', help='Creates a gist, data took from stdin or a file',
        args=(
            json_arg,
            command_arg('-f', '--file',
                help='Create gist from file, otherwise will use stdin',
                type=argparse.FileType('r'),
                default=sys.stdin),
            command_arg('-gn', '--gist_name',
                help='The name of the file to create. Will try to take --file\'s filename if not precised.',
            ),
            command_arg('-desc', '--description',
                help='Description of the gist to create',
            ),
            command_arg('--public',
                help='Creates a public gist',
                action='store_true',
            )
        ))
    def create(self, file, description, json=False, public=False,  gist_name=None):
        content = "".join(file.readlines())
        if gist_name is None:
            gist_name = file.name

        req = requests.post(url = "%s/gists" % self.API_URL,
            headers=self.auth_header(),
            params=self.scope_params(),
            data=JSON.dumps({ "description": description,
                "public": public,
                "files": {
                    gist_name: {
                        "content": content
                    }
                }
            }))
        data = req.json()
        result = {
            'url': data['html_url'],
            'api_url': data['url'],
            'id': data['id'],
            gist_name: data['files'][gist_name]['raw_url']
        }
        if json:
            print(self.as_json(result))
        else:
            print("Created gist at %s" % result['url'])
            print("\n".join(list(
                map(
                    lambda k: "%s: %s" % (k, result[k]),
                    result.keys()
                )
            )))

# triggers command parsing from argparse.
api = GistApi().parse_args()


def init(): return GistApi()
