from urllib.request import urlopen
import subprocess
import difflib
import pprint
import click
import ssl
import sys
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


def run(cmd, _in):
    """Run `cmd` passing `_in` to stdin"""
    proc = subprocess.run(
        args            = cmd,
        input           = ''.join(_in),
        encoding        = 'utf-8',
        capture_output  = True,
        check           = True,
        timeout         = 1.5    # seconds
    )
    return proc


def pretty_diff_ans(a, b):
    """Compare `a` and `b` returning a list of ANSI styled string
    and a boolean indicating if `a` and `b` are equal"""
    d = difflib.ndiff(a, b)
    ret = []
    equal = True
    for s in d:
        if s.startswith('- '):
            ret.append(click.style(s, fg='red'))
        elif s.startswith('? '):
            equal = False
            ret.append(click.style(s, fg='cyan'))
        else:
            ret.append(click.style(s, fg='green'))
    return ret, equal


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
        click.echo(f"URL:\t\t\"{url['url']}\"")
        click.echo(f"Prog:\t\t\"{prog}\"")

    try:
        tests = download_tests(url['url'])
        click.echo(f'Test Cases:\t{len(tests)}\n')
    except TestsNotFoundError:
        click.echo(f"> No test files found at \"{url['url']}\".")
        sys.exit(1)

    for test in tests:
        try:
            click.echo(click.style(f">> TEST {test['id']}", fg='yellow'))
            result = run(prog, test['in'])

            if verbose:
                click.echo(
                    click.style('> Input:', bold=True) +
                    '\n' +
                    pp.pformat(test['in'])
                )
                click.echo(
                    '\n' +
                    click.style('> Output:', bold=True) +
                    '\n' +
                    pp.pformat(result.stdout.splitlines(keepends=True)) +
                    '\n'
                )

            diff, equal = pretty_diff_ans(
                result.stdout.splitlines(keepends=True),
                test['sol']
            )

            if nodiff:
                msg = 'OK' if equal else 'Wrong Answer'
                fg = 'green' if equal else 'red'
                click.secho('> ' + msg, fg=fg)
                continue

            click.echo(
                click.style('> Diff:', bold=True) +
                '\n' +
                ''.join(diff)
            )
        except subprocess.TimeoutExpired as e:
            click.echo(f'> Timeout of {e.timeout}s expired while waiting for program "{e.cmd}".')
        except subprocess.CalledProcessError as e:
            click.echo(f'> Program "{e.cmd}" returned non-zero exit status {e.returncode}.')
        except Exception as e:
            click.echo('> Unexpected error:\n')
            click.echo(e)
            sys.exit(1)
