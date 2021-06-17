import click
import re

class SusyURLValidator(click.ParamType):
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


@click.command()
@click.option('-n', '--nodiff', is_flag=True, help='Disable output diff.')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output.')
@click.version_option()
@click.argument('url', type=SusyURLValidator())
@click.argument('prog', type=click.Path(exists=True, dir_okay=False))
def cli(url, prog, nodiff, verbose):
    """A script to automate the testing of programs to be
    submitted to Unicamp's SuSy platform."""
    if verbose:
        click.echo("URL:\t" + url['url'])
        click.echo("Prog:\t" + prog)
