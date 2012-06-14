'''
Created on Aug 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the integration of the additional arguments into the main arguments.
'''

from ally.api.type import Input, typeFor
from ally.core.spec.resources import Invoker, Path
from ally.design.context import defines, Context, requires
from ally.design.processor import Handler, processor, Chain

# --------------------------------------------------------------------

class RequestProvide(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Defined
    argumentsOfType = defines(dict, doc='''
    @rtype: dictionary{Type, object}
    A dictionary containing as a key the argument type, this dictionary needs to be populated by the 
    processors with any system values that might be used for invoking, the actual use of this arguments depends
    ''')

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(Path)
    invoker = requires(Invoker)
    argumentsOfType = requires(dict)
    # ---------------------------------------------------------------- Defined
    arguments = defines(dict, doc='''
    @rtype: dictionary{string, object}
    The dictionary containing the arguments that will be passes to the invoker that provides the response object.
    ''')

# --------------------------------------------------------------------

class ArgumentsHandler(Handler):
    '''
    Implementation for a processor that provides the integration of the additional arguments into the invoke arguments.
    '''

    @processor
    def provide(self, chain, request:RequestProvide, **keyargs):
        '''
        Provides the additional arguments by type to be populated.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, RequestProvide), 'Invalid request %s' % request

        request.argumentsOfType = {}

        chain.proceed()

    @processor
    def build(self, chain, request:Request, **keyargs):
        '''
        Transpose the additional arguments into the main arguments.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        if Request.arguments not in request: request.arguments = {}

        if request.argumentsOfType:
            for inp in request.invoker.inputs:
                assert isinstance(inp, Input), 'Invalid input %s' % inp

                if inp.name in request.arguments: continue

                for argType, value in request.argumentsOfType.items():
                    if typeFor(argType) == inp.type:
                        request.arguments[inp.name] = value
                        break

        request.arguments.update(request.path.toArguments(request.invoker))

        chain.proceed()
