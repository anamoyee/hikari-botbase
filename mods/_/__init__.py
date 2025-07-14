from datetime import datetime

from prelude import *
from tcrutils.language import nth

from ._version import __version__

logger = get_logger(__name__)


async def load() -> None:
	from common.events import ModsLoadedEvent

	...

	from . import lang

	...  # Load translations first

	from mods._ import commands, db, events, hooks, models
	from mods._ import config as _config

	@ModsLoadedEvent.subscribe
	async def on_mods_loaded(event: ModsLoadedEvent):
		await events.DatabaseInitEvent().emit_excgroup()
		await events.DatabaseInitedEvent().emit_excgroup()

	@events.DatabaseInitedEvent.subscribe
	async def on_database_inited(event: events.DatabaseInitedEvent):
		with db.GlobalDB() as dbglobal, db.VersionDB(__version__) as dbversion:
			dbversion.current_revolution += 1
			logger.info(f"On the dawn of our {nth(dbversion.current_revolution)} revolution...")

			dbversion.last_boot_datetime = datetime.now(tz=_config.S.TZINFO)

			dbglobal.last_boot_datetime = dbversion.last_boot_datetime
