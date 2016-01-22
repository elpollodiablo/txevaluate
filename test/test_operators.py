from txevaluate import Evaluator, AND, OR, NOT, TRUE, FALSE, ELEMENT_OF, EQUAL
from twisted.internet import defer
from twisted.trial import unittest


def sync_dynamic_argument_str():
	return "test"

def sync_dynamic_argument_true():
	return True

def sync_dynamic_argument_false():
	return False

def sync_dynamic_argument_expression():
	return OR(FALSE(),TRUE())

def sync_dynamic_argument_list():
	return ["el1", "el2", "el3", "test"]

def async_dynamic_argument_str():
	return defer.succeed("test")

def async_dynamic_argument_list():
	return defer.succeed(["el1", "el2", "el3", "test"])

def async_dynamic_argument_true():
	return defer.succeed(True)

def async_dynamic_argument_false():
	return defer.succeed(False)

def async_dynamic_argument_expression():
	return defer.succeed(OR(FALSE(),TRUE()))
	
fixed_value_args = {
	"fixed_arg_list": ["el1", "el2", "el3", "test"],
	"fixed_arg_str": "test",
	"fixed_arg_true" : True,
	"fixed_arg_false" : False,
}

dynamic_args = {
	"sync_dynamic_arg_list" : sync_dynamic_argument_list,
	"sync_dynamic_arg_str" : sync_dynamic_argument_str,
	"sync_dynamic_arg_true" : sync_dynamic_argument_true,
	"sync_dynamic_arg_false" : sync_dynamic_argument_false,
	"sync_dynamic_arg_expr" : sync_dynamic_argument_expression,
	"async_dynamic_arg_list" : async_dynamic_argument_list,
	"async_dynamic_arg_str" : async_dynamic_argument_str,
	"async_dynamic_arg_false" : async_dynamic_argument_false,
	"async_dynamic_arg_true" : async_dynamic_argument_true,
	"async_dynamic_arg_expr" : async_dynamic_argument_expression,
}

class OperatorTest(unittest.TestCase):
	def setUp(self):
		self.evaluator = Evaluator(
			dynamic_args=dynamic_args,
			fixed_value_args=fixed_value_args
		)
		
	def run_test(self, expression, expected_result):
		expression_d = self.evaluator.evaluate(expression)
		expression_d.addCallback(self.assertEquals, expected_result)
		return expression_d
	
	def test_false(self):
		return self.run_test(FALSE(), False)

	def test_true(self):
		return self.run_test(TRUE(), True)

	def test_and_arg_count(self):
		self.failureResultOf(
			self.run_test(AND(), False),
			ValueError
		)
		self.failureResultOf(
			self.run_test(AND(TRUE()), False),
			ValueError
		)
		self.run_test(
			AND(TRUE(),TRUE()),
			True
		)
		self.run_test(
			AND(TRUE(),TRUE(),TRUE(),TRUE()),
			True
		)
	def test_or_arg_count(self):
		self.failureResultOf(
			self.run_test(OR(), False),
			ValueError
		)
		self.failureResultOf(
			self.run_test(OR(TRUE()), False),
			ValueError
		)
		self.run_test(
			OR(TRUE(),TRUE()),
			True
		)
		self.run_test(
			OR(TRUE(),TRUE(),TRUE(),TRUE()),
			True
		)
	def test_or(self):
		return defer.DeferredList([
			self.run_test(
				OR(FALSE(),TRUE(),AND(TRUE(),TRUE())),
				True
			),
			self.run_test(
				AND(TRUE(),TRUE(),OR(TRUE(),FALSE())),
				True
			),
			self.run_test(OR(FALSE(), FALSE(), FALSE(), FALSE()),
				False
			)
		])
	def test_or(self):
		return defer.DeferredList([
			self.run_test(
				OR(FALSE(),TRUE(),AND(TRUE(),TRUE())),
				True
			),
			self.run_test(
				AND(TRUE(),TRUE(),OR(TRUE(),FALSE())),
				True
			),
			self.run_test(OR(FALSE(), FALSE(), FALSE(), FALSE(), TRUE()),
				True
			),
			self.run_test(OR(TRUE(), FALSE(), FALSE(), FALSE(), FALSE()),
				True
			)
		])
	def test_and(self):
		return defer.DeferredList([
			self.run_test(
				AND(TRUE(),TRUE(),AND(TRUE(),TRUE())),
				True
			),
			self.run_test(
				AND(TRUE(),TRUE(),AND(TRUE(),FALSE())),
				False
			),
			self.run_test(AND(FALSE(), TRUE(), TRUE(), TRUE(), TRUE()),
				False
			),
			self.run_test(AND(TRUE(), TRUE(), TRUE(), TRUE(), FALSE()),
				False
			)
		])

	def test_not_arg_count(self):
		with self.assertRaises(TypeError):
			self.run_test(NOT(), False)

		with self.assertRaises(TypeError):
			self.run_test(NOT(TRUE(), TRUE()), False)

	def test_not(self):
		return defer.DeferredList([
			self.run_test(
				NOT(FALSE()),
				True
			),
			self.run_test(
				NOT(TRUE()),
				False
			),
			self.run_test(
				NOT(OR(TRUE(), FALSE())),
				False
			),
			self.run_test(
				NOT(AND(TRUE(),TRUE(),AND(TRUE(),FALSE()))),
				True
			),
		])
	def test_equal(self):
		return defer.DeferredList([
			self.run_test(
				EQUAL("value", "value"),
				True
			),
			self.run_test(
				EQUAL("value", "othervalue"),
				False
			)
		])
	def test_elementof(self):
		return defer.DeferredList([
			self.run_test(
				ELEMENT_OF("value", ["value", "othervalue"]),
				True
			),
			self.run_test(
				ELEMENT_OF("value", ["othervalue", "yetanothervalue"]),
				False
			)
		])
	def test_elementof_sync_dynamic_arg(self):
		return defer.DeferredList([
			self.run_test(
				ELEMENT_OF("el1", "sync_dynamic_arg_list"),
				True
			),
			self.run_test(
				ELEMENT_OF("sync_dynamic_arg_str", "sync_dynamic_arg_list"),
				True
			),
		])
	def test_elementof_async_dynamic_arg(self):
		return defer.DeferredList([
			self.run_test(
				ELEMENT_OF("el1", "async_dynamic_arg_list"),
				True
			),
			self.run_test(
				ELEMENT_OF("async_dynamic_arg_str", "async_dynamic_arg_list"),
				True
			),
		])
	def test_equal_dynamic_arg(self):
		return defer.DeferredList([
			self.run_test(
				EQUAL("sync_dynamic_arg_str", "async_dynamic_arg_str"),
				True
			),
			self.run_test(
				ELEMENT_OF("fixed_arg_str", "async_dynamic_arg_list"),
				True
			),
		])
	def test_all_bool(self):
		return defer.DeferredList([
			self.run_test(
				AND("sync_dynamic_arg_true", "async_dynamic_arg_true",
					 'fixed_arg_true', NOT("sync_dynamic_arg_false"),
					 NOT("async_dynamic_arg_false"),  NOT("fixed_arg_false"),
					 TRUE(), NOT(FALSE()), True),
				True
			),
			self.run_test(
				OR(NOT("sync_dynamic_arg_true"), NOT("async_dynamic_arg_true"),
				NOT('fixed_arg_true'), "sync_dynamic_arg_false",
				"async_dynamic_arg_false",  "fixed_arg_false", FALSE(),
				NOT(TRUE()), False),
				False
			),
		])
	def test_fixed_values(self):
		return defer.DeferredList([
			self.run_test(
				AND("fixed_arg_true", TRUE()),
				True
			),			
			self.run_test(
				AND("fixed_arg_false", TRUE()),
				False
			),
			self.run_test(
				ELEMENT_OF("doesntexist", "fixed_arg_list"),
				False
			),
			self.run_test(
				ELEMENT_OF("test", "fixed_arg_list"),
				True
			),
		])