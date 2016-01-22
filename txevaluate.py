from twisted.internet import defer
from twisted.python import log

def OR(*args):
    l = ['_op_or']
    l.extend(args)
    return l
    
def AND(*args):
    l = ['_op_and']
    l.extend(args)
    return l

def NOT(arg):
    return ['_op_not', arg]

def TRUE(*args):
    return ['_op_true']

def FALSE(*args):
    return ['_op_false']

def ELEMENT_OF(el, el_l):
    return ['_op_elof', el, el_l]

def EQUAL(el1, el2):
    return ["_op_equal", el1, el2]

class Evaluator():
    ops = {}
    def __init__(self, dynamic_args ={}, fixed_value_args = {}):
        #print "evaluator init"
        self.dynamic_args = dynamic_args
        self.fixed_value_args = fixed_value_args

    def _translate_arg(self, arg):
        #print "translate", arg
        translated_arg = self.dynamic_args.get(
             str(arg),
             lambda *ignored_args, **ignored_kws:
                 self.fixed_value_args.get(str(arg), arg))()
        if (isinstance(translated_arg, defer.Deferred)
            or isinstance(translated_arg, defer.DeferredList)):
            return translated_arg
        elif type(translated_arg) == type(list()) and hasattr(self, arg[0]):
            #print "seems to be an operator too", translated_arg
            return self._call_op_real(translated_arg[0], *translated_arg[1:])
        else:
            # a deferredlist only accepts deferreds - make this one
            return defer.succeed(translated_arg)

    def _translate_args(self, args):
        return [_translate_arg(arg) for arg in args]

    def _call_op_real(self, op, *args):
        #print "call_op_real", op, args
        if op in (True, False, None):
            return defer.succeed(op or False)

        if hasattr(self, op):
            return getattr(self, op)(*args)
        else:
            log.err("no such operand: %s" % op)
            raise Exception()

    def _call_op(self, expression):
        if expression in (True, False, None):
            return defer.succeed(expression or False)
        def handle_expression_cb(result):
            if result in (True, False, None):
                return defer.succeed(result or False)
            op = result[0]
            args = result[1:]
            return self._call_op_real(op, *args)            
        # two cases:
        # a) we get a real expression (a list)
        # b) we get a deferred. deal with both!
        if (isinstance(expression, defer.Deferred)):
            expression.addCallback(handle_expression_cb)
            return expression
        else:
            op = expression[0]
            args = expression[1:]
            return self._call_op_real(op, *args)
            
    def _op_not(self, expression):
        #print "not", expression
        def op_not_cb(expression):
            #print "in not returning", expression, not expression
            return not expression
        expression_d = self._call_op(self._translate_arg(expression))
        expression_d.addCallback(op_not_cb)
        return expression_d

    def _op_or(self, *expressions):
        if len(expressions) < 2:
            raise ValueError("operator OR needs at least two operands")
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

    def _op_and(self, *expressions):
        if len(expressions) < 2:
            raise ValueError("operator AND needs at least two operands")
        def and_cb(result, expressions):
            #print "result and expressions", result, expressions
            if not result:
                #print "not result, False"
                return False
            elif not expressions:
                # we're the last result - if result is not false,
                # no remaining means...
                #print "not expressions, True"
                return True
            else:
                exp = expressions[0]
                remaining_exp = expressions[1:]
                #print "calling"
                call_result_d = defer.maybeDeferred(self._call_op, self._translate_arg(exp))
                call_result_d.addCallback(and_cb, remaining_exp)
                return call_result_d
        return and_cb(True, expressions)
    
    def _op_elof(self, el, el_l):
        #print "elof", el, el_l
        translated_el = self._translate_arg(el)
        translated_el_l = self._translate_arg(el_l)
        def elof_cb(result):
            success, el = result[0]
            success, el_l = result[1]
            return el in el_l
        dl = defer.DeferredList([translated_el, translated_el_l])
        dl.addCallback(elof_cb)
        return dl

    def _op_equal(self, el1, el2):
        translated_el1 = self._translate_arg(el1)
        translated_el2 = self._translate_arg(el2)
        def equal_cb(result):
            success, el1 = result[0]
            success, el2 = result[1]
            return el1 == el2
        dl = defer.DeferredList([translated_el1, translated_el2])
        dl.addCallback(equal_cb)
        return dl

    def _op_true(self, *ignored):
        return True
    
    def _op_false(self, *ignored):
        return False

    def evaluate(self, expression, dynamic_args = None):
        #print "evaluating"
        self.dynamic_args = dynamic_args if dynamic_args else self.dynamic_args
        r = defer.maybeDeferred(self._call_op, expression)
        #print "returning r", r
        return r