from ..txevaluate import Evaluator, AND, OR, NOT, TRUE, FALSE, ELEMENT_OF
from twisted.internet import defer

if __name__ == "__main__":
    test_exps = [
        (OR(FALSE(), defer.succeed(["true"])), True),
        (OR(defer.succeed(TRUE()), defer.succeed(FALSE()), "never"), True),
        (OR(defer.succeed(FALSE()), defer.succeed(FALSE())), False),
        (AND(defer.succeed(TRUE()), NOT(defer.succeed(TRUE()))), False),
        (AND(defer.succeed(TRUE()), defer.succeed(TRUE())), True),
        (AND(ELEMENT_OF("x", ["x", "y", "z"]), ELEMENT_OF("x", "sdl"),defer.succeed(TRUE())), False),
        (AND(ELEMENT_OF("x", ["x", "y", "z"]), ELEMENT_OF("a", "sdl"),defer.succeed(TRUE())), True),
    ]

    def never_executed():
        print "Execution stops before this is printed"
        return defer.succeed(TRUE())

    def some_deferred_list():
        # let's pretend we were getting that from a database
        return defer.succeed(["a", "b", "c"])

    def eval_result(result, original_exp, expected_result):
        if result != expected_result:
            print "test failed", original_exp, result

    txeval = Evaluator(dynamic_args={"sdl": some_deferred_list, "never":never_executed})

    for exp, exp_result in test_exps:
        eval_d = txeval.evaluate(exp)
        eval_d.addCallback(eval_result, exp, exp_result)