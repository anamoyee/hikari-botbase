from prelude import *
from tcrutils.decorator import instance as _instance


@_instance
class S(BM):
	DEV_IDS: set[int] = {507642999992352779}
	"""Users from this set will be able to execute developer commands from this mod."""

	DEV_GUILDS: set[int] = {1145433323594842166}
	"""Guilds from this set will receive the dev command registration messages."""
