from abc import ABCMeta, abstractmethod
from .exceptions import (DFEmptyError, MissingColumnError, WrongDtypeError, ColumnNullError,
                         ColumnNotUniqueError, ColumnNotSingleValueError)


class ReturnValueDecorator(metaclass=ABCMeta):

    def __call__(self, fcn):
        """ To be used as function decorator. """
        def inner(*args, **kwargs):
            result = fcn(*args, **kwargs)
            return self.validate(result)
        
        return inner

    @abstractmethod
    def validate(self, value):
        """ Validates the return value of the decorated function. May be called directly on a value. """
        pass


class NotEmpty(ReturnValueDecorator):

    def __init__(self, allow_none=False, allow_scalar=True):
        """ Raises DFEmpty if the return value has a length of 0 or is None.

        :param bool allow_none: make None a valid return value.
        :param bool allow_scalar: do not raise if the return value has no length. """
        self.allow_none = allow_none
        self.allow_scalar = allow_scalar
        
    def validate(self, value):
        if value is None:
            if not self.allow_none:
                raise DFEmptyError('return value is None')
            return None
        try:
            if not len(value):
                raise DFEmptyError('value is empty %s' % type(value))
        except TypeError:
            if not self.allow_scalar:
                raise DFEmptyError('value is of scalar type %r' % type(value))
        return value


class HasColumn(ReturnValueDecorator):

    def __init__(self, columns, allow_none=False, allow_empty=False):
        """ Raises MissingColumnError if a column in the result is missing.

        :param iterable columns: list of columns
        :param bool allow_none: make None a valid return value.
        :param bool allow_empty: allow a DataFrame of length zero, if it has the required columns
        """
        self.columns = set(columns)
        self.allow_none = allow_none
        self.allow_empty = allow_empty

    def _validate_has_columns(self, value):
        try:
            missing_columns = self.columns - set(value.columns)
        except AttributeError:
            raise AttributeError('Return value of type "%s" does not must have the "columns" attribute. '
                                 '(expected DataFrame)' % type(value))
        if len(missing_columns):
            raise MissingColumnError('missing columns: ' + ','.join(missing_columns))

    def _validate_empty(self, value):
        if not len(value):
            if self.allow_empty:
                return True
            else:
                raise DFEmptyError('Return value of type %s has length 0.' % type(value))
        return False

    def _validate_details(self, value, is_empty):
        pass

    def validate(self, value):
        if value is None:
            if not self.allow_none:
                raise DFEmptyError('Return value must not be None.')
            return None
        self._validate_has_columns(value)
        is_empty = self._validate_empty(value)
        self._validate_details(value, is_empty)
        return value


class ColumnHasDtype(HasColumn):

    def __init__(self, dtypes, allow_none=False, allow_empty=False):
        """ Raises WrongDtypeError if the returned DataFrame has columns of wrong type.

        :param dict dtypes: pairs column name with expected dtype.
        :param bool allow_none: make None a valid return value.
        :param bool allow_empty: allow a DataFrame of length zero, if it has the required columns
        """
        super(ColumnHasDtype, self).__init__([x for x in dtypes], allow_none=allow_none, allow_empty=allow_empty)
        self.dtypes = {x: y for x, y in dtypes.items()}  # type check on creation

    def _validate_details(self, value, is_empty):
        wrong_dtypes = []
        for column, dtype in self.dtypes.items():
            if value[column].dtype != dtype:
                wrong_dtypes.append(column)
        if len(wrong_dtypes):
            raise WrongDtypeError('Columns with wrong dtypes: ' + ', '.join('%s: %s (expected %s)' % (
                column, value[column].dtype, self.dtypes[column]
            ) for column in wrong_dtypes))


class ColumnNotNull(HasColumn):

    def __init__(self, col_notnull, allow_none=False, allow_empty=False):
        """ Raises ColumnNullError if the returned DataFrame has columns that contain null elements.

        :param dict col_notnull: pairs column name with expected content: 'all' if all values must not be null,
            'any' if one or more values must not be null.
        :param bool allow_none: make None a valid return value.
        :param bool allow_empty: allow a DataFrame of length zero, if it has the required columns
        """
        super(ColumnNotNull, self).__init__([x for x in col_notnull], allow_none=allow_none, allow_empty=allow_empty)
        self.notnull = {x: y for x, y in col_notnull.items()}  # type check on creation

    def _validate_details(self, value, is_empty):
        if is_empty:
            return
        wrong_content = []
        null_per_column = value.isnull().sum()
        notnull_all = [colname for colname in null_per_column[null_per_column == 0].index]
        notnull_any = [colname for colname in null_per_column[null_per_column < len(value)].index]
        for column, notnull in self.notnull.items():
            if notnull == 'any':
                if column not in notnull_any:
                    wrong_content.append(column)
            if notnull == 'all':
                if column not in notnull_all:
                    wrong_content.append(column)
        if len(wrong_content):
            raise ColumnNullError('Unexpected Null values in columns of length %i: ' % len(value) +
                                  ', '.join('%s: %i (not null expected: %s)' % (
                                      column, null_per_column.loc[column], self.notnull[column]
                                  ) for column in wrong_content))


class ColumnUnique(HasColumn):

    def _validate_details(self, value, is_empty):
        if is_empty:
            return
        for col in self.columns:
            duplicates = value[col].duplicated()
            if duplicates.any():
                raise ColumnNotUniqueError(
                    'Column %s is not unique! First duplicate item: %r' % (col, value[col][duplicates].iloc[0]))


class ColumnSingleValue(HasColumn):

    def _validate_details(self, value, is_empty):
        if is_empty:
            return
        for col in self.columns:
            if value[col].nunique() > 1:
                raise ColumnNotSingleValueError(
                    'Column %s has multiple values! First two values: %r' % (col, value[col].unique()[:2]))
