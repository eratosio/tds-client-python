
import unicodedata

try:
    from numpy import unicode
except ImportError:
    # latter numpy stores unicode in the compat namespace.
    from numpy.compat import unicode

def normalise(val):
    if val is not None:
        val = unicodedata.normalize('NFKD', unicode(val))

        try:
            val = val.casefold()  # Python 3.3+
        except AttributeError:
            val = val.upper().lower()  # Older Pythons

        return unicodedata.normalize('NFKD', unicode(val))
