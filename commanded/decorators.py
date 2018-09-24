import argparse

from commanded.utils import as_obj

def command_arg(*args, **kwargs):
    """
    Small tweak to build argparse.add_argument() arguments through a command
    declaration (see `command` decorator and `Command.add_arguments` method)
    """
    class CommandArg:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def get_name(self):
            name = self.args[1] if len(self.args) > 1 else self.args[0]
            if name.startswith('--'):
                name = name[2:]
            return name
    return CommandArg(*args, **kwargs)


class Command(object):
    """
    The Command object represent a given action. In fine, its goal is to make
    the argparse.ArgumentParser parsing result in the calling of the method that
    used the @command decorator.
    """
    def __init__(self, name, help, args, f):
        self.help = help
        self.name = name
        self.args = args
        self.f = f

    def __call__(self, instance, *args, **kwargs):
        return self.f(instance, *args, **kwargs)

    def has_arguments(self):
        return len(self.args) > 0

    def add_arguments(self, parser):
        for arg in self.args:
            parser.add_argument(*arg.args, **arg.kwargs)

    # Takes args produced by argparse.parse_args() and outputs the proper kwargs
    # dict for the bound api method.
    def process_kwargs(self, args):
        kwargs = {}
        for arg in self.args:
            argname = arg.get_name()
            if getattr(args, argname, False):
                kwargs[argname] = getattr(args, argname)
        return kwargs

def command(name='', help=None, args=list()):
    """
    @command() decorator. Used to register a sub command for argparse.
    To register arguments just use the command_arg() helper as you would with
    parser.add_argument() arguments.
    """
    def decorated(func): return Command(name=name, help=help, args=args, f=func)
    return decorated

def with_commands(description, *args, **kwargs):
    """
    Register a class as a commanded class. All methods marked with the @command()
    decorator will be be piloted from here.
    """
    def wrapped(Cls):
        class CommandedCls:
            def __init__(self, *args, **kwargs):
                self.instance = Cls(*args, **kwargs)
                self.parser = argparse.ArgumentParser(description=description, *args, **kwargs)
                self.__add_commands()

            def __getattribute__(self, attr):
                _attr = None
                try: _attr = super(CommandedCls, self).__getattribute__(attr)
                except: pass
                if _attr is None:
                    _attr = self.instance.__getattribute__(attr)
                return _attr

            def __add_commands(self):
                bindings = self.list_bindings()
                subparsers = self.parser.add_subparsers()
                for key, command in bindings.items():
                    command_parser = subparsers.add_parser(key, help=command.help)
                    command_parser.set_defaults(command=key)
                    command.add_arguments(command_parser)
                self.bindings = bindings

            def list_bindings(self):
                """
                Will return all decorated methods as a dict:
                { <command name>: <bound command object>, <other command name>: <other command>, .. }
                """
                def is_valid_name(name): return not name.startswith('__')
                def is_decorated(name): return isinstance(getattr(self.instance, name), Command)

                all_command_names = filter(is_decorated, filter(is_valid_name, dir(self.instance)))
                commands = map(lambda name: getattr(self.instance, name), all_command_names)
                return {
                    command.name: command for command in commands
                }

            def parse_args(self):
                args = self.parser.parse_args()
                if args.command:
                    command = self.bindings.get(args.command)
                    kwargs = command.process_kwargs(args)
                    return command(self.instance, **kwargs)
                    # method execution
                else:
                    self.parser.print_help()
                    return False

        return CommandedCls
    return wrapped
