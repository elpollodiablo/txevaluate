from txevaluate import Evaluator, AND, OR, NOT, TRUE, FALSE, ELEMENT_OF
from twisted.internet import defer

# create an expression
will_survive = lambda who: (OR(
	AND(
		ELEMENT_OF(who, "heart_of_gold"), 
		ELEMENT_OF(who, "get_ape_descendants"),
		# make sure earth still exists
		TRUE(),
	),
        # since we're in an OR clause, this will never be executed if the
        # other condition is true. 
	NOT("meaning_of_life"),
))

def never_executed():
	print "Execution may stop before this is printed"
	return True

def some_database_request():
	# let's pretend we were getting that from a database
	return defer.succeed(["arthur", "trillian", "barkeeper"])

fixed_value_args = {
	"heart_of_gold": ["arthur", "ford", "zaphod", "trillian"]
}

dynamic_args = {
	"get_ape_descendants" : some_database_request,
	"meaning_of_life" : never_executed
}

# create an objected loaded with dynamic arguments (that will only be evaluated when needed)
txeval = Evaluator(dynamic_args=dynamic_args, fixed_value_args=fixed_value_args)

def eval_result_cb(result, who):
	if result:
		print who

# evaluate
eval_arthur_d = txeval.evaluate(will_survive("arthur"))
eval_barkeeper_d = txeval.evaluate(will_survive("barkeeper"))
eval_arthur_d.addCallback(eval_result_cb, "arthur")
eval_barkeeper_d.addCallback(eval_result_cb,"barkeeper")
