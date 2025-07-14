from common import Event


class DatabaseInitEvent(Event[None]):
	"""Represents the event-hook for mods to add to the databse pydantic models by overriding the _.db.* ones, make sure to make them compatible. The DB is accessible AFTER this event is finished."""

class DatabaseInitedEvent(Event[None]):
	"""The database can now be accessed after this event."""
