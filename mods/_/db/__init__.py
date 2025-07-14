from datetime import datetime

from prelude import *
from tcrutils.sdb2 import ShelfManager, SingleShelfManager

from ..config import S
from . import model_global, model_guild, model_profile, model_user, model_version
from .model_profile import ProfileID


class UserDB(ShelfManager[model_user.User]):
	PATH = S.DB_DIRECTORY / "users"

	def default_factory(self) -> str:
		return model_user.User()


class GuildDB(ShelfManager[model_guild.Guild]):
	PATH = S.DB_DIRECTORY / "guilds"

	def default_factory(self) -> str:
		return model_guild.Guild()


class VersionDB(ShelfManager[model_version.Version]):
	PATH = S.DB_DIRECTORY / "versions"

	def default_factory(self):
		return model_version.Version()


class GlobalDB(SingleShelfManager[model_global.Global]):
	PATH = S.DB_DIRECTORY / "global"

	def default_factory(self):
		return model_global.Global()
