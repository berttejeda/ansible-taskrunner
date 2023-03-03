# Imports
import click
import sys
from ansible_taskrunner.logger import Logger

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

# Allow for mutually-exlusive click options
class NotRequiredIf(click.Option):

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                if self.name == self.not_required_if:
                    logger.error(f"Option order error: `{self.name}`")
                    logger.error("Make sure you call this option BEFORE any mutually-exlusive options referencing it")
                    logger.error("Check your tasks manifest")
                    sys.exit(1)
                else:
                    logger.error(
                        f"Illegal usage: `{self.name}` is mutually exclusive with `{self.not_required_if}`")
                    sys.exit(1)
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)
