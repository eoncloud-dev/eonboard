# HERE FORMATING AS shown in:
# LIST: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT="Y-m-d H:i" 
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'F j'
SHORT_DATE_FORMAT = 'm/d/Y'
SHORT_DATETIME_FORMAT = 'm/d/Y P'
FIRST_DAY_OF_WEEK = 1

# BUT here use the Python strftime format syntax,
# LIST: http://docs.python.org/library/datetime.html#strftime-strptime-behavior

DATE_INPUT_FORMATS = (
    '%Y-%m-%d',     # '2014-01-12'
)
TIME_INPUT_FORMATS = (
    '%H:%M:%S',     # '17:59:59'
    '%H:%M',        # '17:59'
)
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',     # '21-03-2014 17:59'
)

DECIMAL_SEPARATOR = u'.'
THOUSAND_SEPARATOR = u','
NUMBER_GROUPING = 3
