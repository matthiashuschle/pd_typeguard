class ReturnValueError(Exception):
    """ Superclass for detailed exceptions. """
    pass


class DFEmptyError(ReturnValueError):
    """ Method returns None or empty object. """
    pass


class MissingColumnError(ReturnValueError):
    """ Method returns DataFrame without required column. """
    pass


class WrongDtypeError(ReturnValueError):
    """ Return value has wrong Dtypes. """
    pass


class ColumnNullError(ReturnValueError):
    """ A column is unexpectedly empty. """
    pass


class ColumnNotUniqueError(ReturnValueError):
    """ A column is unexpectedly not unique. """
    pass


class ColumnNotSingleValueError(ReturnValueError):
    """ A column contains more than one distinct values. """
    pass
