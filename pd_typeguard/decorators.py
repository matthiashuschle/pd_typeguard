from abc import ABCMeta, abstractmethod
from .exceptions import DFEmptyError, MissingColumnError


class ReturnValueDecorator(metaclass=ABCMeta):

    def __call__(self, fcn):
        """ To be used as function decorator. """
        def inner(*args, **kwargs):
            result = fcn(*args, **kwargs)
            return self.validate(result)
        
        return inner

    @abstractmethod
    def validate(self, value):
        pass


class NonEmpty(ReturnValueDecorator):

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

    def __init__(self, columns):
        """ Raises MissingColumnError if a column in the result is missing.

        :param iterable columns: list of columns
        """
        self.columns = set(columns)

    def validate(self, value):
        try:
            missing_columns = self.columns - set(value.columns)
            if len(missing_columns):
                raise MissingColumnError('missing columns: ' + ','.join(missing_columns))
        except AttributeError:
            raise MissingColumnError('return value of type %s has no attribute "columns".' % type(value))
        return value
