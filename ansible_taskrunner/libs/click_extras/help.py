# Imports
import click
from ansible_taskrunner.logger import Logger

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class ExtendedEpilog(click.Group):
    def format_epilog(self, ctx, formatter):
        """Format click epilog to honor newline characters"""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split('\n'):
                formatter.write_text(line)

class ExtendedHelp(click.Command):

    def colorize(self, formatter, color, string):
        if color == 'green':
            formatter.write_text('%s' % click.style(string, fg='bright_green'))
        elif color == 'magenta':
            formatter.write_text('%s' % click.style(string, fg='bright_magenta'))
        elif color == 'red':
            formatter.write_text('%s' % click.style(string, fg='bright_red'))
        elif color == 'yellow':
            formatter.write_text('%s' % click.style(string, fg='bright_yellow'))
        else:
            formatter.write_text(string)

    def format_help(self, ctx, formatter):
        """Format click help to honor newline characters"""
        if self.help:
            formatter.write_paragraph()
            for line in self.help.split('\n'):
                formatter.write_text(line)
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)
        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split('\n'):
                if line:
                    if line.startswith('-'):
                        self.colorize(formatter, 'magenta', line)
                    else:
                        self.colorize(formatter, 'yellow', line)
                else:
                    formatter.write_text(line)
