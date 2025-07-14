from collections.abc import Callable

from common.bot import BOT
from prelude import *
from tcrutils.language import apostrophe_s

from ..errors import UserGetsDetailsError
from ..models import GetByHashSet
from . import model_profile
from .model_profile import ProfileID


class UnableToEnsureProfileError(UserGetsDetailsError):
	"""User().ensure_profile() was called, but user has profiles, yet none are selected (bug or raw data alteration went wrong??)."""


class User(BM):
	selected_profile_id: ProfileID | None = pd.Field(default=None)
	profiles: GetByHashSet[model_profile.Profile] = pd.Field(default_factory=GetByHashSet)

	@property
	def selected_profile(self) -> model_profile.Profile:
		"""Get the currently selected profile for this account as a mutable object to update (or just read).

		Raises RuntimeError if this account does not have any profiles selected (`.has_selected_profile()`).
		"""
		if not self.has_selected_profile():
			raise RuntimeError("This account does not have any profile selected. This happens when an account has no profiles or due to a bug.")
		return self.profiles[self.selected_profile_id]

	def has_selected_profile(self) -> bool:
		"""Whether or not this account has a valid selected profile. This is false only if this account has no profiles or has profiles but by eval/exec it was set to None or a bug in code is present."""
		return self.selected_profile_id is not None

	def select_profile(self, profile_id: ProfileID | model_profile.Profile) -> tuple[model_profile.Profile, bool]:
		"""Change the selected profile in this account to this profile by the Profile object or by the ProfileID enum variant. Return that profile and whether it was NOT necessary to switch (if the profile was already the selected profile) as a 2-el tuple.

		Raises ValueError if the user does not have this profile.
		"""

		if isinstance(profile_id, model_profile.Profile):
			profile_id = profile_id.id

		already_this_profile = self.is_selected(profile_id)

		try:
			profile = self.get_profile_by_id(profile_id)
		except KeyError as e:
			raise ValueError(f"Attempted to select a non-existent on this account profile: {profile_id!r}.") from e

		if not already_this_profile:
			self.selected_profile_id = profile.id

		return profile, already_this_profile

	def get_profile_by_id(self, profile_id: ProfileID) -> model_profile.Profile:
		"""Return the profile of a given profile_id, raise KeyError if not found on user."""
		try:
			return [prof for prof in self.profiles if prof.id == profile_id][0]  # noqa: RUF015
		except IndexError as e:
			raise KeyError(profile_id) from e

	def has_profile_by_id(self, profile_id: ProfileID) -> bool:
		return any(prof.id == profile_id for prof in self.profiles)

	def is_selected(self, profile_id: ProfileID | model_profile.Profile) -> bool:
		if isinstance(profile_id, model_profile.Profile):
			profile_id = profile_id.id

		return self.selected_profile_id == profile_id

	def create_profile(
		self,
		*,
		owner: hikari.SnowflakeishOr[hikari.PartialUser],
		profile_id: ProfileID | None = None,
	) -> model_profile.Profile:
		"""Create a new Profile with the given ProfileID and a default name, add it to the profiles set and return it. Will raise a ValueError if ran out of profile IDs."""
		if profile_id is None:
			profile_id = ProfileID.get_random(p.id for p in self.profiles)

		new_profile = model_profile.Profile(id=profile_id)

		new_profile.display_name = f"{apostrophe_s(owner.display_name)} Profile"

		# Nothing will be added if the profile of the same ID already exists
		self.profiles.add(new_profile)

		if not self.has_selected_profile():  # If that is the first profile of this account (or otherwise the current profile is not set), set it to it
			self.selected_profile_id = profile_id

		return new_profile

	def ensure_profile(self, ctx: arc.GatewayContext) -> model_profile.Profile:
		"""Ensure a profile is selected, if not - create one if there are no profiles, if everything went okay return that Profile.

		**!!! If there's at least 1 profile, but none is selected, raise UnableToEnsureProfileError with a bug message to the user**.

		## Usage:
		```
		with UserDB(ctx.author.id) as user:
			profile = await user.ensure_profile(ctx)
			# then use profile and not user.selected_profile
		```
		"""
		if not self.has_selected_profile():
			if self.profiles:
				raise UnableToEnsureProfileError("Huh... it looks like you have profiles, but dont have a profile selected..? Report this as a bug, or try re-selecting with /profiles")

			return self.create_profile(owner=ctx.author)  # This also auto-selects the profile if none are selected already

		return self.selected_profile

	### str formatting ###########################

	def make_profiles_display_list(
		self,
		selected_fn: Callable[[str], str] = lambda s: f"**{s}**",
		unselected_fn: Callable[[str], str] = lambda s: s,
	) -> str:
		return "\n".join(
			(selected_fn if self.is_selected(prof) else unselected_fn)(prof.make_md_ident_name())
			for prof in sorted(
				self.profiles,
				key=model_profile.Profile.sort_key,
			)
		)
