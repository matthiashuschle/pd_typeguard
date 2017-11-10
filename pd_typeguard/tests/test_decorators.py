from unittest import TestCase
from ..decorators import (ReturnValueDecorator, NotEmpty, HasColumn, ColumnHasDtype,
                          ColumnNotNull, ColumnUnique, ColumnSingleValue)
from ..exceptions import (DFEmptyError, MissingColumnError, WrongDtypeError, ColumnNullError,
                          ColumnNotUniqueError, ColumnNotSingleValueError)

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

        @NotEmpty()
        def mirror(value):
            return value

        self.assertRaises(DFEmptyError, mirror, None)
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertIsNotNone(mirror(1))
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

    def test_decorator_accept_none(self):

        @NotEmpty(allow_none=True)
        def mirror(value):
            return value

        self.assertIsNone(mirror(None))
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertIsNotNone(mirror(1))
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

    def test_decorator_refuse_scalar(self):

        @NotEmpty(allow_scalar=False)
        def mirror(value):
            return value

        self.assertRaises(DFEmptyError, mirror, None)
        self.assertRaises(DFEmptyError, mirror, [])
        self.assertRaises(DFEmptyError, mirror, pd.DataFrame())
        self.assertRaises(DFEmptyError, mirror, 1)
        self.assertIsNotNone(mirror([1]))
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))
        
    def test_validate_default(self):
        validate = NotEmpty().validate
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

        self.assertRaises(DFEmptyError, mirror, None)
        self.assertRaises(AttributeError, mirror, [])
        self.assertRaises(AttributeError, mirror, {})
        self.assertRaises(MissingColumnError, mirror, pd.DataFrame())
        self.assertRaises(AttributeError, mirror, 1)
        self.assertRaises(AttributeError, mirror, [1])
        self.assertRaises(AttributeError, mirror, {1})
        self.assertIsNotNone(mirror(pd.DataFrame({'a': [1]})))

        @HasColumn(['c', 'a', 'd'])
        def mirror(value):
            return value

        self.assertRaises(DFEmptyError, mirror, pd.DataFrame(columns=['a', 'b', 'c', 'd']))
        self.assertRaises(MissingColumnError, mirror, pd.DataFrame(columns=['a', 'b', 'd']))

        @HasColumn(['c', 'a', 'd'], allow_empty=True)
        def mirror(value):
            return value

        self.assertIsNotNone(mirror(pd.DataFrame(columns=['a', 'b', 'c', 'd'])))
        self.assertRaises(MissingColumnError, mirror, pd.DataFrame(columns=['a', 'b', 'd']))

    def test_validate_default(self):
        validate = HasColumn(['a']).validate
        self.assertRaises(DFEmptyError, validate, None)
        self.assertRaises(MissingColumnError, validate, pd.DataFrame())
        self.assertIsNotNone(validate(pd.DataFrame({'a': [1]})))
        validate = HasColumn(['c', 'a', 'd']).validate
        self.assertRaises(DFEmptyError, validate, pd.DataFrame(columns=['a', 'b', 'c', 'd']))
        self.assertRaises(MissingColumnError, validate, pd.DataFrame(columns=['a', 'b', 'd']))
        validate = HasColumn(['c', 'a', 'd'], allow_empty=True).validate
        self.assertIsNotNone(validate(pd.DataFrame(columns=['a', 'b', 'c', 'd'])))
        self.assertRaises(MissingColumnError, validate, pd.DataFrame(columns=['a', 'b', 'd']))
        validate = HasColumn(['a'], allow_none=True).validate
        self.assertIsNone(validate(None))
        validate = HasColumn(['c', 'a', 'd'], allow_none=True, allow_empty=True).validate
        self.assertIsNotNone(validate(pd.DataFrame(columns=['a', 'b', 'c', 'd'])))
        self.assertRaises(MissingColumnError, validate, pd.DataFrame(columns=['a', 'b', 'd']))
        self.assertIsNone(validate(None))


class TestColumnHasDtype(TestCase):

    def test_validate_default(self):
        validate = ColumnHasDtype({}).validate
        self.assertRaises(DFEmptyError, validate, None)
        validate = ColumnHasDtype({}, allow_none=True).validate
        self.assertEqual(validate(None), None)
        validate = ColumnHasDtype({'intcol': 'int64'}).validate
        self.assertRaises(DFEmptyError, validate, None)
        df_valid = pd.DataFrame({'moo': ['a', 'b'], 'intcol': [1, 2]})
        self.assertIs(df_valid, validate(df_valid))
        df_invalid = pd.DataFrame({'intcol': ['a', 'b'], 'moo': [1, 2]})
        self.assertRaises(WrongDtypeError, validate, df_invalid)
        validate = ColumnHasDtype({'intcol': 'int64'}, allow_none=True).validate
        self.assertEqual(validate(None), None)
        self.assertIs(df_valid, validate(df_valid))
        self.assertRaises(WrongDtypeError, validate, df_invalid)
        validate = ColumnHasDtype({'intcol': 'int64', 'moo': 'object'}).validate
        self.assertRaises(DFEmptyError, validate, None)
        self.assertIs(df_valid, validate(df_valid))
        self.assertRaises(WrongDtypeError, validate, df_invalid)


class TestColumnNotNull(TestCase):

    def test_validate_default(self):
        validate = ColumnNotNull({}).validate
        self.assertRaises(DFEmptyError, validate, None)

        validate = ColumnNotNull({}, allow_none=True).validate
        self.assertEqual(validate(None), None)
        del validate

        df_a_all = pd.DataFrame({'a': [1, 2], 'b': [None, None]})
        df_a_any = pd.DataFrame({'a': [1, None], 'b': [None, None]})
        df_a_null = pd.DataFrame({'a': [None, None], 'b': [None, None]})
        df_empty = df_a_null.head(0)
        validate_any = ColumnNotNull({'a': 'any'}).validate
        validate_all = ColumnNotNull({'a': 'all'}).validate
        self.assertRaises(DFEmptyError, validate_any, None)
        self.assertRaises(MissingColumnError, validate_any, pd.DataFrame())
        self.assertRaises(DFEmptyError, validate_any, df_empty)
        self.assertRaises(DFEmptyError, validate_all, None)
        self.assertRaises(MissingColumnError, validate_all, pd.DataFrame())
        self.assertRaises(DFEmptyError, validate_all, df_empty)
        self.assertIs(df_a_all, validate_any(df_a_all))
        self.assertIs(df_a_all, validate_all(df_a_all))
        self.assertIs(df_a_any, validate_any(df_a_any))
        self.assertRaises(ColumnNullError, validate_all, df_a_any)
        self.assertRaises(ColumnNullError, validate_any, df_a_null)
        self.assertRaises(ColumnNullError, validate_all, df_a_null)

        validate_any = ColumnNotNull({'a': 'any'}, allow_empty=True).validate
        validate_all = ColumnNotNull({'a': 'all'}, allow_empty=True).validate
        self.assertRaises(DFEmptyError, validate_any, None)
        self.assertRaises(DFEmptyError, validate_all, None)
        self.assertRaises(MissingColumnError, validate_any, pd.DataFrame())
        self.assertRaises(MissingColumnError, validate_all, pd.DataFrame())
        self.assertIs(df_empty, validate_any(df_empty))
        self.assertIs(df_a_all, validate_any(df_a_all))
        self.assertIs(df_a_all, validate_all(df_a_all))
        self.assertIs(df_a_any, validate_any(df_a_any))
        self.assertRaises(ColumnNullError, validate_all, df_a_any)
        self.assertRaises(ColumnNullError, validate_any, df_a_null)
        self.assertRaises(ColumnNullError, validate_all, df_a_null)


class TestColumnUnique(TestCase):

    def test_validate_default(self):
        validate = ColumnUnique({}).validate
        self.assertRaises(DFEmptyError, validate, None)

        validate = ColumnUnique({}, allow_none=True).validate
        self.assertEqual(validate(None), None)

    def test_validate_simple(self):
        df_valid = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y'], 'c': ['z', 'z']})
        validate = ColumnUnique(['a', 'b']).validate
        self.assertIs(df_valid, validate(df_valid))
        validate = ColumnUnique(['a', 'c']).validate
        self.assertRaises(ColumnNotUniqueError, validate, df_valid)
        validate = ColumnUnique(['c']).validate
        self.assertRaises(ColumnNotUniqueError, validate, df_valid)


class TestColumnSingleValue(TestCase):

    def test_validate_default(self):
        validate = ColumnSingleValue({}).validate
        self.assertRaises(DFEmptyError, validate, None)

        validate = ColumnSingleValue({}, allow_none=True).validate
        self.assertEqual(validate(None), None)

    def test_validate_simple(self):
        df_valid = pd.DataFrame({'a': [1, 2], 'b': ['x', 'x'], 'c': ['z', 'z']})
        validate = ColumnSingleValue(['a']).validate
        self.assertRaises(ColumnNotSingleValueError, validate, df_valid)
        validate = ColumnSingleValue(['a', 'c']).validate
        self.assertRaises(ColumnNotSingleValueError, validate, df_valid)
        validate = ColumnSingleValue(['c']).validate
        self.assertIs(df_valid, validate(df_valid))
        validate = ColumnSingleValue(['b', 'c']).validate
        self.assertIs(df_valid, validate(df_valid))
