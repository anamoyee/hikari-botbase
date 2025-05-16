from prelude import *
from tcrutils.aevents import BaseEvent


class Event(BM, BaseEvent): ...


class ModsLoadedEvent(Event): ...
