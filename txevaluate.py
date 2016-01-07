from twisted.internet import defer
from twisted.python import log

def OR(*args):
    l = ['||']
    l.extend(args)
    return l
    
def AND(*args):
    l = ['&&']
    l.extend(args)
    return l

def NOT(arg):
    return ['!', arg]

def TRUE():
    return ['true']

def FALSE():
    return ['false']

def ELEMENT_OF(el, el_l):
    return ['E', el, el_l]

class Evaluator():
    ops = {}
    def __init__(self, dynamic_args ={}, fixed_value_args = {}):
        self.dynamic_args = dynamic_args
        self.fixed_value_args = fixed_value_args

    def _translate_arg(self, arg):
         translated_arg = self.dynamic_args.get(
             str(arg),
             lambda *ignored_args, **ignored_kws:
                 self.fixed_value_args.get(str(arg), arg))()
         if (isinstance(translated_arg, defer.Deferred)
             or isinstance(translated_arg, defer.DeferredList)):
             return translated_arg
         else:
             # a deferredlist only accepts deferreds - make this one
             return defer.succeed(translated_arg)

    def _translate_args(self, args):
        return [_translate_arg(arg) for arg in args]

    def _call_op(self, expression):
        if isinstance(expression, bool):
            return expression

        def handle_expression_cb(result):
            if isinstance(result, bool):
                return result
            op = result[0]
            args = result[1:]
            return self.ops[op](self, * args)            
        # two cases:
        # a) we get a real expression (a list)
        # b) we get a deferred. deal with both!
        if (isinstance(expression, defer.Deferred)):
            expression.addCallback(handle_expression_cb)
            return expression
        else:
            op = expression[0]
            args = expression[1:]
            return self.ops[op](self, * args)
            
    def _op_not(self, expression):
        return not self._call_op(self._translate_arg(expression))
    ops["!"] = _op_not

    def _op_or(self, *expressions):
        def or_cb(result, expressions):
            if result:
                #print "true result was", result
                return True
            elif not expressions:
                # we're the last result - if result is False,
                # no remaining means...
                return False
            else:
                exp = expressions[0]
                remaining_exp = expressions[1:]
                call_result_d = defer.maybeDeferred(self._call_op, self._translate_arg(exp))
                call_result_d.addCallback(or_cb, remaining_exp)
                return call_result_d
        return or_cb(False, expressions)
    ops["||"] = _op_or

    def _op_and(self, *expressions):
        def and_cb(result, expressions):
            if not result:
                return False
            elif not expressions:
                # we're the last result - if result is not false,
                # no remaining means...
                return True
            else:
                exp = expressions[0]
                remaining_exp = expressions[1:]
                call_result_d = defer.maybeDeferred(self._call_op, self._translate_arg(exp))
                call_result_d.addCallback(and_cb, remaining_exp)
                return call_result_d
        return and_cb(True, expressions)
    ops["&&"] = _op_and
    
    def _op_elof(self, el, el_l):
        translated_el = self._translate_arg(el)
        translated_el_l = self._translate_arg(el_l)
        def elof_cb(result):
            success, el = result[0]
            success, el_l = result[1]
            return el in el_l
        dl = defer.DeferredList([translated_el, translated_el_l])
        dl.addCallback(elof_cb)
        return dl
    ops["E"] = _op_elof

    def _op_true(self, *ignored):
        return True
    ops["true"] = _op_true
    
    def _op_false(self, *ignored):
        return False
    ops["false"] = _op_false

    def evaluate(self, expression, dynamic_args = None):
        self.dynamic_args = dynamic_args if dynamic_args else self.dynamic_args
        r = defer.maybeDeferred(self._call_op, expression)
        return r