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


class TestsNotFoundError(Exception):
    """No test cases files found on web page"""
    pass


def match_files(html):
    """Extract test file names from HTML source"""
    try:
        end = re.search(r'Testes fechados', html).end()
        matches = re.findall(r'"(arq\d.\w+)"', html[ : end])
    except AttributeError:
        raise TestsNotFoundError

    if len(matches) < 2:
        raise TestsNotFoundError

    files = [tuple(matches[i:i+2]) for i in range(0, len(matches), 2)]
    return files


def download_tests(url):
    """Download test cases files (input/solution)"""
    def _download(url):
        with urlopen(url, context=ssl.SSLContext(ssl.PROTOCOL_TLS)) as response:
            return response.read().decode()

    html = _download(url + '/dados/testes.html')
    files = match_files(html)
    tests = []
    for i, val in enumerate(files):
        _in, _sol = val
        t = {
            'id': i,
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

    try:
        tests = download_tests(url['url'])
        click.echo('Test Cases:\n' + pp.pformat(tests))
    except TestsNotFoundError:
        click.echo(f"No test files found at \"{url['url']}\".")
