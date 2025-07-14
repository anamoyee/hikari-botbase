from prelude import *
from tcrutils.aevents import BaseEvent


class Event[T](BM, BaseEvent[T]): ...


class ModsLoadedEvent(Event[None]): ...
