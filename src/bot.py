import sys
from traceback import print_exc

from common import BOT
from common.events import ModsLoadedEvent
from prelude import *
from src.mod_loader import MODS, ModDependencyError, load_mods_from_directory
from tcrutils.extract_error import print_exception_with_traceback

if sys.modules.get("__global_loaded_bot.py__"):
	raise RuntimeError(
		"Tried to load bot.py twice! This is a bug. Try to import either relatively or absolutely but not both at the same time. This leads to multiple event listeners which breaks stuff down the line and all that shit."
	)

sys.modules["__global_loaded_bot.py__"] = True


@BOT.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent):
	if "_" in sys.modules:  # Prevent duplicate fire
		return

	try:
		try:
			MODS.update(await load_mods_from_directory(p.Path(__file__).parent.parent / "mods"))
		except ModDependencyError as e:
			c.critical(f"mods: {e}")
			exit(1)

		await ModsLoadedEvent().emit_excgroup()
	except Exception:
		print_exc()
		exit(1)
