import yaml
import requests
from lxml import html as lhtml
from functools import partial
import re

import only_otters.scrapetools.util as util
import only_otters.scrapetools.autobrowser as autobrowser


class Keywords:
    class Root:
        url: str = 'url'
        dynamic: bool = 'dynamic'
        content: dict = 'content'

    class Query:
        location: str = 'loc'
        properties: dict = 'properties'
        body: dict = 'body'

        prefix: str = 'prefix'
        suffix: str = 'suffix'
        postfix: str = 'finally'

    class Properties:
        propagation: str = 'propagate_queries'
        pipes: str = 'pipes'


class HierarchicalXPathQuery:
    """
    A class allowing you to make dict-like XPath queries.

    The best way to use this would be to store your query
    in a separate yaml file and create a new object with
    the 'from_yml' class method.

    This class comes with default pipes and modes, but you
    can extend them with the class methods of the same, which
    behave as decorators.
    """

    # --------------------------------------------------------------------------
    # Default pipes.
    # Use <class>.pipe to register a function as a new pipe.
    # Said function must take only one argument, e.g. 'item'.
    # --------------------------------------------------------------------------
    PIPES = {
        'single': util.one_or_many,
        'astype': util.astype,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'tuple': tuple,
        'flatten': util.flatten,
        'isnumeric': str.isnumeric,
        'isalpha': str.isalpha,
        'isalnum': str.isalnum,
        'print': lambda a: print(a) or a,
        'strip': str.strip,
        'upper': str.upper,
        'lower': str.lower,
        'title': str.title,
        'capitalize': str.capitalize,
        'is': lambda x: x,
        'bool': bool
    }

    # --------------------------------------------------------------------------
    # Default higher-order pipes.
    # Extensible with <class>.high_pipe (decorator)
    # Said function must take two arguments: a callable and an iterable.
    # --------------------------------------------------------------------------
    HIGHER_ORDER_PIPES = {
        'map': map,
        'filter': filter,
        'lmap': lambda f, n: list(map(f, n)),
        'lfilter': lambda f, n: list(filter(f, n)),
        'lcomp': lambda f, n: [f(_) for _ in n]
    }

    # --------------------------------------------------------------------------
    # Default modes.
    # Modes are pipes that are fixed at the end of the pipeline.
    # --------------------------------------------------------------------------
    MODES = {
        's': str,
        'l': list,
        'u': util.one_or_many
    }

    # --------------------------------------------------------------------------
    # Default higher-horder modes.
    # --------------------------------------------------------------------------
    HIGHER_ORDER_MODES = {
        'm': lambda f, gen: list(map(f, gen)),
        'f': lambda f, gen: list(filter(f, gen))
    }

    # --------------------------------------------------------------------------

    def resolve_mode(self, name: str, high: bool = False) -> callable:
        """Return mode from name. If high is true, look in higher-order modes list."""
        mode = (self.MODES if not high else self.HIGHER_ORDER_MODES).get(name)
        if mode is None:
            raise UserWarning('No such %smode: %s' % ('higher-order ' * high, name))
        return mode

    def resolve_pipe(self, name: str) -> callable:
        """
        Return pipe from name.
        If pipe has format 'a:b', return left member higher-order pipe partial
        upon pipe.
        If high is true, look in higher-order pipes list.
        """
        if ':' in name:
            hopipename, pipename = name.split(':', maxsplit=1)

            hopipe = self.HIGHER_ORDER_PIPES.get(hopipename)
            pipe = self.PIPES.get(pipename)

            if hopipe is None:
                raise UserWarning('No such high-order pipe: %s' % hopipename)

            if pipe is None:
                raise UserWarning('No such pipe: %s' % pipename)

            return partial(hopipe, pipe)

        pipe = self.PIPES.get(name)
        if pipe is None:
            raise UserWarning('No such pipe: %s' % name)

        return pipe

    def resolve_pipe_expr(self,
                          expr: str,
                          pipe_prefix: str = None) -> (str, list, list, callable):
        """
        Translate a pipe expression into a multi-function wrapper for a regular
        XPath path expression.

        A pipe expression is always found at the beginning of the expression :

        $ (<higher-order mode>)*:(<mode>){ <function>,+ } <xpath_expr>

        ## Pipes
        The result of the xpath expression found on the right is successively
        passed through the listed functions, from right to left.

        ## Modes
        Modes are found on the left side of the bracket expression.
        They either modify the behavior of each function found between the
        brackets (higher-order modes), or they are simply functions applied
        at the very end of the pipeline (regular modes).

        There can be multiple expressions on the left side of the composite
        expression, but beware they will be combined: modes are merged and
        pipes are concatenated.

        :pipe_prefix
        If not None, 'expr' will be prefixed with this. Intended to be a
        pipe expression.

        """
        if pipe_prefix is not None:
            expr = pipe_prefix + ' ' + expr

        regex = r'^\s*\$\s*([a-z]:)?([a-z]+)?\s*{\s*((?:[\w:]+\s*[,]?\s*)+)\s*}'

        pipes = []
        modes = []
        ho_mode = None
        match = re.match(regex, expr)

        while match is not None:
            _ho_mode, _modes, _pipes = match.groups()

            # TODO: Resolve modes & pipes before runnning Xpath expr

            # Parse modes
            if _ho_mode is not None:
                _ho_mode = _ho_mode.strip(':')
                if len(_ho_mode) > 1 or ho_mode:
                    raise UserWarning('There can only be one \
                        mode of higher-order. %s' % ho_mode)
                ho_mode = self.resolve_mode(_ho_mode, high=True)

            # Parse pipes
            _pipes = _pipes.split(',')
            _pipes = list(map(str.strip, _pipes))

            pipes.extend(_pipes or [])
            modes.extend(_modes or [])

            expr = expr[match.span()[1]:]
            match = re.match(regex, expr)

        # Resolve pipes + ho_mode
        for idx, pipename in enumerate(pipes):
            fn = self.resolve_pipe(pipename)
            if ho_mode is not None:
                fn = partial(ho_mode, fn)
            pipes[idx] = fn

        for idx, mode in enumerate(modes):
            fn = self.resolve_mode(mode)
            modes[idx] = fn

        return expr, pipes[::-1], modes, ho_mode

    def resolve_xpath(self, element, expr: str, pipe_prefix: bool = None):
        """Resolve a composite XPath expression."""
        expr, pipes, modes, _ = self.resolve_pipe_expr(expr,
                                                      pipe_prefix=pipe_prefix)

        result = element.xpath(expr)

        for pipe in pipes:
            result = pipe(result)

        for mode in modes:
            result = mode(result)

        return result

    @util.both_class_instance
    def register_pipe(self, fn: callable, name: str = None, high: bool = False):
        """Register a new pipe function so that it can be used in a query."""
        if name is not None:
            if not re.match(r'^\w+$', name):
                raise UserWarning('{!r} is not a compliant name. \
                    Allowed characters: [a-zA-Z0-9_]'.format(name))
        else:
            name = fn.__name__

        if not high:
            self.PIPES[name] = fn
        else:
            self.HIGHER_ORDER_PIPES[name] = fn

    @util.both_class_instance
    def pipe(self, name: str = None):  # A pipe decorator
        """
        Register a function as a pipe under the specified name.
        If no name is provided, the function __name__ is used instead.
        To accomplish the latter case, this decorator can be used without ().
        """
        if callable(name):
            return self.register_pipe(name)
        return partial(self.register_pipe, name=name)

    @util.both_class_instance
    def high_pipe(self, name: str = None):
        """Register a function as a higher-order pipe."""
        if callable(name):
            return self.register_pipe(name, high=True)
        return partial(self.register_pipe, name=name, high=True)

    def apply_pipes(self, fn: callable, pipe_properties: dict):

        pipes = []

        for name, kargs in pipe_properties.items():

            target = self.PIPES.get(name)
            if target is None:
                raise KeyError('No such pipe function: %s' % name)

            pipes.append(
                partial(target, **kargs)
            )

        if pipes:
            return util.pipe(*pipes)(fn)

        return fn

    def process_query(self, tree, xquery: dict, **properties):

        ##
        postprocess = xquery.pop(Keywords.Query.postfix, None)
        if postprocess is not None:
            _, pipes, _, _ = self.resolve_pipe_expr(postprocess)
            gen = self.process_query(tree, xquery, **properties)
            for pipe in pipes:
                if type(pipe) == partial:
                    gen = pipe(gen)
                else:
                    gen = map(pipe, gen)
            yield from gen
            return
        ##

        loc_query = xquery[Keywords.Query.location]
        query = xquery[Keywords.Query.body]
        prefix = xquery.get(Keywords.Query.prefix)
        suffix = xquery.get(Keywords.Query.suffix)

        # Process properties
        properties = properties or {}
        properties.update(xquery.get(Keywords.Query.properties, {}))

        # Prepare to propagate properties to nested queries
        propagated_properties = {}
        if properties.get(Keywords.Properties.propagation):
            propagated_properties = properties

        process_xpath = self.resolve_xpath

        # Set up the pipes
        pipe_properties = properties.get(Keywords.Properties.pipes)
        if pipe_properties is not None:
            process_xpath = self.apply_pipes(self.resolve_xpath, pipe_properties)

        # Apply prefix if provided
        if prefix is not None:
            process_xpath = partial(process_xpath, pipe_prefix=prefix)

        # Resolve suffix 
        suffix_pipes = []
        if suffix is not None:
            _, suffix_pipes, _, _ = self.resolve_pipe_expr(suffix)

        for loc in tree.xpath(loc_query):

            result = {}

            for key, value in query.items():

                if type(value) == dict:
                    value = [*self.process_query(loc, value, **propagated_properties)]

                elif type(value) in (list, tuple):
                    value = [
                        process_xpath(loc, v)
                        for v in value
                    ]

                else:
                    value = process_xpath(loc, value)

                result[key] = value

            # Apply suffix expression
            for pipe in suffix_pipes:
                result = pipe(result)

            yield result

    @classmethod
    def from_yml(cls, filepath: str):
        """Builds a <class> object from a YAML file."""
        data = yaml.safe_load(open(filepath))
        return cls(**data)

    def __init__(self, *, content: dict, url: str = None, dynamic: bool = False):
        """
        :url
        The url at which we will send a GET request to fetch content we wish to
        scrape data from.

        :content
        The top-level hierarchical query.

        :dynamic
        Whether the source requires a full in-browser experience, with enabled Javascript.

        """
        self.url = url
        self.content = content
        self.dynamic = dynamic

        # Copy class pipes & modes into instance
        self.PIPES = {**self.PIPES}
        self.MODES = {**self.MODES}
        self.HIGHER_ORDER_PIPES = {**self.HIGHER_ORDER_PIPES}
        self.HIGHER_ORDER_MODES = {**self.HIGHER_ORDER_MODES}

    def get(self, url: str = None, dynamic: bool = None) -> str:
        """Fetch the content found at the provided url, and runs the query
        on the HTML received."""
        url = url or self.url

        if dynamic is None:
            dynamic = self.dynamic

        if dynamic:
            return autobrowser.fetch(url)

        response = requests.get(url)
        if response.status_code >= 400:
            raise requests.exceptions.HTTPError(response)

        return response.content

    def __call__(self, url: str = None, html: str = None) -> dict:

        url = url or self.url

        if html is None:
            html = self.get(url)

        tree = lhtml.fromstring(html)

        return self.process_query(tree, self.content)
