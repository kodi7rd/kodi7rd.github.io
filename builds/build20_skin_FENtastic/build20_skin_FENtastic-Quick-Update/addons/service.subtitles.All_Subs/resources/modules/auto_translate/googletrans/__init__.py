"""Free Google Translate API for Python. Translates totally free of charge."""
__all__ = 'Translator',
__version__ = '3.1.0-alpha'


from resources.modules.auto_translate.googletrans.client import Translator
from resources.modules.auto_translate.googletrans.constants import LANGCODES, LANGUAGES  # noqa
