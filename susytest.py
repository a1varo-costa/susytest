from urllib.request import urlopen
import pprint
import click
import ssl
import re

class SusyURLValidator(click.ParamType):
    """Validate URL given as command line argument"""

    regex = r'(https\:\/\/susy\.ic\.unicamp\.br\:9999\/)(\w+)\/(\w+)$'
    example = 'https://susy.ic.unicamp.br:9999/<COURSE>/<EXERCISE>'
    name = 'url'

    def convert(self, value, param, ctx):
        match = re.match(self.regex, value)
        if not match:
            self.fail(
                f'"{value}".\n    > Expected pattern: "{self.example}"',
                param,
                ctx
            )
        value = {
            'url': match.group(0),
            'netloc': match.group(1),
            'course': match.group(2),
            'exercise': match.group(3)
        }
        return value


def match_files(html):
    """Extract test file names from HTML source"""
    end = re.search(r'Testes fechados', html).end()
    matches = re.findall(r'"arq\d.in"|"arq\d.res"', html[ : end])

    files = []
    for i, j in zip(range(len(matches) - 1), range(1, len(matches))):
        t = (matches[i].replace('"', ''), matches[j].replace('"', ''))
        files.append(t)
    return files


def download_tests(url):
    """Download test cases files (input/solution)"""
    def _download(url):
        with urlopen(url, context=ssl.SSLContext(ssl.PROTOCOL_TLS)) as response:
            return response.read().decode()

    html = _download(url + '/dados/testes.html')
    files = match_files(html)
    tests = []
    for _in, _sol in files:
        t = {
            'in': _download(url + '/dados/' + _in).splitlines(keepends=True),
            'sol': _download(url + '/dados/' + _sol).splitlines(keepends=True)
        }
        tests.append(t)
    return tests


@click.command()
@click.option('-n', '--nodiff', is_flag=True, help='Disable output diff.')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output.')
@click.version_option()
@click.argument('url', type=SusyURLValidator())
@click.argument('prog', type=click.Path(exists=True, dir_okay=False))
def cli(url, prog, nodiff, verbose):
    """A script to automate the testing of programs to be
    submitted to Unicamp's SuSy platform."""
    pp = pprint.PrettyPrinter(indent=4, width=79)

    if verbose:
        click.echo("URL:\t" + url['url'])
        click.echo("Prog:\t" + prog)

    tests = download_tests(url['url'])

    i = 0
    for test in tests:
        click.echo(f'==== TEST {i}====')
        click.echo('Input:\n' + pp.pformat(test['in']))
        click.echo('Solution:\n' + pp.pformat(test['sol']))
        i += 1
