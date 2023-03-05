# Imports
import click
from ansible_taskrunner.logger import Logger

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

# Allow for click options that are mutually inclusive
# to another, related, option
class RequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.required_if = set(kwargs.pop('required_if', []))
        assert self.required_if, "'required_if' parameter required"
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.required_if.intersection(opts) and self.name in opts
        other_present = self.required_if.intersection(opts)

        if other_present:
            if we_are_present:
                pass
            else:
                self.required = True
                self.prompt = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)

# Allow for click options that are not required if
# another, related option is specified
class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = set(kwargs.pop('not_required_if', []))
        assert self.not_required_if, "'not_required_if' parameter required"
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.not_required_if.intersection(opts) and self.name in opts
        other_present = self.not_required_if.intersection(opts)

        if other_present:
            if we_are_present:
                pass
            else:
                self.required = False
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

# Allow for mutually-exclusive click options
class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.help = kwargs.get('help')
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.exceptions.UsageError(
                f"Illegal usage! As per --help: {self.help}"
            )
        else:
            pass

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )
