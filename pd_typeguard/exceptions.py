class DFEmptyError(Exception):
    """ Method returns None or empty object. """
    pass


class MissingColumnError(Exception):
    """ Method returns DataFrame without required column. """
    pass


class WrongDtypeError(Exception):
    """ Return value has wrong Dtypes. """
    pass


class ColumnNullError(Exception):
    """ A column is unexpectedly empty. """
    pass
