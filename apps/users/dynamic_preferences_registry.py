from dynamic_preferences.types import (
    StringPreference,
    IntegerPreference,
    FloatPreference,
)
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from blob.utils.customClasses import PreferenceMixin


settings = Section('settings')


@global_preferences_registry.register
class WithdrawPercentage(PreferenceMixin, FloatPreference):
    section = settings
    name = 'withdraw_percentage'
    default = 0.8


@global_preferences_registry.register
class RequestsPerUserForFree(PreferenceMixin, IntegerPreference):
    section = settings
    name = 'requests_per_user_for_free'
    default = 10
