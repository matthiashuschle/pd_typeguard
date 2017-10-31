from unittest import TestCase
# from unittest.mock import Mock
from ..decorators import ReturnValueDecorator, NonEmpty, HasColumn
from ..exceptions import DFEmptyError, MissingColumnError
import pandas as pd


class TestReturnValueDecorator(TestCase):

    def test_validation(self):

        class ReturnValueTestDecorator(ReturnValueDecorator):

            def __init__(self):
                self.n_called = 0
                self.values = []

            def validate(self, value):
                self.n_called += 1
                self.values.append(value)
                return value

        decorator = ReturnValueTestDecorator()

        @decorator
        def mirror(value):
            return str(value)

        result = mirror(1)
        self.assertEqual(result, '1')
        self.assertEqual(1, decorator.n_called)
        self.assertEqual(['1'], decorator.values)


class TestNonEmpty(TestCase):

    def test_decorator_default(self):

        @NonEmpty()
        def mirror(value):
            return value

        self.assertRaises(DFEmptyError, mirror, None)
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertIsNotNone(mirror(1))
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

    def test_decorator_accept_none(self):

        @NonEmpty(allow_none=True)
        def mirror(value):
            return value

        self.assertIsNone(mirror(None))
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertIsNotNone(mirror(1))
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

    def test_decorator_refuse_scalar(self):

        @NonEmpty(allow_scalar=False)
        def mirror(value):
            return value

        self.assertRaises(DFEmptyError, mirror, None)
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertRaises(DFEmptyError, mirror, 1)
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))
        
    def test_validate_default(self):
        validate = NonEmpty().validate
        self.assertRaises(DFEmptyError, validate, None)
        self.assertRaises(DFEmptyError, validate, [])
        self.assertRaises(DFEmptyError, validate, pd.DataFrame())
        self.assertIsNotNone(validate(1))
        self.assertIsNotNone(validate([1]))
        self.assertIsNotNone(validate(pd.DataFrame({'a': [1]})))


class TestHasColumn(TestCase):

    def test_decorator_default(self):

        @HasColumn(['a'])
        def mirror(value):
            return value

        self.assertRaises(MissingColumnError, mirror, None)
        self.assertRaises(MissingColumnError, mirror, [])
        self.assertRaises(MissingColumnError, mirror, {})
        self.assertRaises(MissingColumnError, mirror, pd.DataFrame())
        self.assertRaises(MissingColumnError, mirror, 1)
        self.assertRaises(MissingColumnError, mirror, [1])
        self.assertRaises(MissingColumnError, mirror, {1})
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

        @HasColumn(['c', 'a', 'd'])
        def mirror(value):
            return value

        self.assertIsNotNone(mirror(pd.DataFrame(columns=['a', 'b', 'c', 'd'])))
        self.assertRaises(MissingColumnError, mirror, pd.DataFrame(columns=['a', 'b', 'd']))

    def test_validate_default(self):
        validate = HasColumn(['a']).validate
        self.assertRaises(MissingColumnError, validate, None)
        self.assertRaises(MissingColumnError, validate, [])
        self.assertRaises(MissingColumnError, validate, {})
        self.assertRaises(MissingColumnError, validate, pd.DataFrame())
        self.assertRaises(MissingColumnError, validate, 1)
        self.assertRaises(MissingColumnError, validate, [1])
        self.assertRaises(MissingColumnError, validate, {1})
        self.assertIsNotNone(validate(pd.DataFrame({'a': [1]})))
        validate = HasColumn(['c', 'a', 'd']).validate
        self.assertIsNotNone(validate(pd.DataFrame(columns=['a', 'b', 'c', 'd'])))
        self.assertRaises(MissingColumnError, validate, pd.DataFrame(columns=['a', 'b', 'd']))
