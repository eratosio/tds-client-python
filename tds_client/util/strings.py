
import unicodedata


def normalise(val):
    if val is not None:
        val = unicodedata.normalize('NFKD', val)

        try:
            val = val.casefold()  # Python 3.3+
        except AttributeError:
            val = val.upper().lower()  # Older Pythons

        return unicodedata.normalize('NFKD', val)
