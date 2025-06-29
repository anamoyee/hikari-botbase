import re as regex

from common import ACL, BOT, MCL
from miru import Modal, ModalContext, ViewContext
from miru.ext.menu import Menu, Screen, ScreenButton, ScreenContent, ScreenTextSelect
from prelude import *

from ..config import S
from ..db import Profile, ProfileID, UserDB
from ..errors import UserGetsDetailsError
from ..lang import LANG
from ..tools.loopback_link import make_loopback
from ..tools.menus import CopycatScreen, DisableItemsOnTimeoutMenu, MultipleStartingScreenStackMenu, OwnedMenu, OwnedScreenButton, OwnedScreenTextSelect, enforce_owned_callback

if True:  # autocomplete

	def _profile_search_key(key: str, profile: Profile) -> bool:
		key = key.casefold()

		if key in profile.display_name.casefold():
			return True

		if key in profile.id.value.casefold():  # noqa: SIM103
			return True

		return False

	def _autocomplete_profile(data: arc.AutocompleteData) -> list[str]:
		with UserDB(data.user.id) as user:
			return [prof.make_ident_name() for prof in user.profiles if _profile_search_key(str(data.focused_value), prof)]


if True:  # errors

	class TooManyProfilesToFitInSelectMenuError(UserGetsDetailsError):
		"""Too many profiles to fit in select menu (somehow the user has >=26 profiles)."""


if True:  # Screen
	if True:  # ProfilesListScreen

		@enforce_owned_callback
		class ProfileSelect(OwnedScreenTextSelect):
			def __init__(self, *, profiles: set[Profile], let_create_new_profile: bool = True) -> None:
				if (n_profiles := len(profiles)) >= 25:
					let_create_new_profile = False

				super().__init__(
					placeholder="Change profile...",
					options=(
						*[
							miru.SelectOption(
								label=prof.make_ident_name(),
								value=prof.id.value,
								emoji=hikari.UnicodeEmoji(prof.emoji),
							)
							for prof in sorted(profiles, key=Profile.sort_key)
						],
						*(
							(
								miru.SelectOption(
									label="New profile",
									value="+",
									emoji=hikari.UnicodeEmoji("➕"),  # noqa: RUF001
								),
							)
							if let_create_new_profile
							else ()
						),
					)[:25],  # failsafe
				)

				if n_profiles > 25:
					raise TooManyProfilesToFitInSelectMenuError(
						f"Somehow you have `{n_profiles}` profiles (over the limit) this is not supported due to Discord limitations (more than 25 options cannot be attached to a select menu)."
					)

			async def callback(self, ctx: ViewContext) -> None:
				selected = self.values[0]

				if selected == "+":  # "new profile"
					await self.menu.push(NewProfileScreen(self.menu, ctx=ctx))
				else:
					await self.menu.push(ProfileScreen(self.menu, ctx=ctx, profile_id=ProfileID.try_from_str(selected)))

		class ProfilesListScreen(Screen):
			prev_ctx: arc.GatewayContext

			def __init__(self, menu: Menu, *, ctx: arc.GatewayContext) -> None:
				super().__init__(menu)

				self.prev_ctx = ctx

				with UserDB(ctx.author.id) as user:
					user.ensure_profile(ctx)

					self.add_item(ProfileSelect(profiles=user.profiles, let_create_new_profile=True))

			async def build_content(self) -> ScreenContent:
				with UserDB(self.prev_ctx.author.id) as user:
					user.ensure_profile(self.prev_ctx)

					return ScreenContent(
						embed=hikari.Embed(
							title=None,
							description=user.make_profiles_display_list(selected_fn=lambda s: make_loopback(self.prev_ctx, f"**{s}**", tip="This profile is currently selected")),
							color=S.COLOR.PRIMARY,
						).set_author(
							name=self.prev_ctx.author.display_name,
							icon=self.prev_ctx.author.make_avatar_url() or self.prev_ctx.author.default_avatar_url,
						),
					)

	if True:  # ProfileScreen

		@enforce_owned_callback
		class PopScreenButton(OwnedScreenButton):
			def __init__(self) -> None:
				super().__init__(label="<<", style=hikari.ButtonStyle.SECONDARY)

			async def callback(self, ctx: ViewContext) -> None:
				await self.menu.pop()

		class ProfileSwitchedSuccessfulCopycatScreen(CopycatScreen):
			def __init__(self, menu: Menu, *, already_selected: bool) -> None:
				super().__init__(menu, copycat_items=False)  # Don't lug the items over, duh
				self.already_selected = already_selected

			async def build_content(self):
				sc = await super().build_content()

				if not self.already_selected:
					return sc.append_embed(
						hikari.Embed(
							title="Profile changed!",
							description="You have successfully switched profiles.",
							color=S.COLOR.SUCCESS,
						)
					)
				else:
					return sc.append_embed(
						hikari.Embed(
							title="Already on that profile!",
							description="You are already on that profile.",
							color=S.COLOR.FAILURE,
						)
					)

		@enforce_owned_callback
		class SwitchToProfileButton(OwnedScreenButton):
			def __init__(self, profile_id: ProfileID, *, already_selected: bool) -> None:
				self.profile_id = profile_id

				if not already_selected:
					super().__init__(label="Change profile!", style=hikari.ButtonStyle.SUCCESS)
				else:
					super().__init__(label="Already selected!", style=hikari.ButtonStyle.SUCCESS, disabled=True)

			async def callback(self, ctx: ViewContext) -> None:
				with UserDB(ctx.author.id) as user:
					_, already_selected = user.select_profile(self.profile_id)

				await self.menu.push(ProfileSwitchedSuccessfulCopycatScreen(self.menu, already_selected=already_selected))

		class DeleteProfileConfirmationModal(miru.Modal):
			def __init__(self, username: str, profile_id: ProfileID, *, view_ctx: ViewContext):
				self.view_ctx = view_ctx
				self.profile_id = profile_id

				super().__init__("Confirm profile deletion")

				self.username_profile = miru.TextInput(label="Confirm which profile to delete", placeholder=f"{username}/{profile_id}", style=hikari.TextInputStyle.SHORT, required=True)
				self.yes_do_as_i_say = miru.TextInput(
					label="This will unrecoverably delete that profile",
					placeholder=(yes_do_as_i_say_str := "Yes, do as I say!"),
					max_length=len(yes_do_as_i_say_str),
					min_length=len(yes_do_as_i_say_str),
					style=hikari.TextInputStyle.SHORT,
					required=True,
				)

				self.add_item(self.username_profile)
				self.add_item(self.yes_do_as_i_say)

			async def callback(self, ctx: ModalContext) -> None:
				if self.username_profile.value != self.username_profile.placeholder:
					await ctx.respond(f"{S.NO} You did not enter the same username or profile ID as the one you tried deleting. Try again with the correct values.")
					return

				if self.yes_do_as_i_say.value != self.yes_do_as_i_say.placeholder:
					await ctx.respond(f"{S.NO} You did not enter the correct confirmation, if you're sure enter exactly `Yes, do as I say!` (capitalization, spaces and punctuation matter).")
					return

				content = f"🗑️ **Successfuly deleted profile `{self.profile_id}`**! RIP\n"

				with UserDB(ctx.author.id) as user:
					prof = user.get_profile_by_id(self.profile_id)

					user.profiles.remove(prof)

					if user.profiles and user.selected_profile_id == self.profile_id:
						user.selected_profile_id = next(iter(user.profiles)).id

						content += f" Since you deleted your currently selected profile you've been bumped off to `{user.selected_profile_id}`."

				if not user.profiles:
					# that was the last profile
					content += " Since that was your last profile, your data has been removed from the database. Farewell 🫡"  # :saluting_face:

					UserDB.delitem_unchecked(ctx.author.id)

				await ctx.respond(content.strip())

		@enforce_owned_callback
		class DeleteProfileButton(OwnedScreenButton):  # TODO: add checks to make it not delete or switch or whatever if the db user isnt the ctx user... pls dont forget this...
			messages = ["Delete", "Are you sure?", "This cant be undone!"]
			profile_id: ProfileID

			def __init__(self, profile_id: ProfileID):
				self.profile_id = profile_id

				super().__init__(label=self.messages[0], style=hikari.ButtonStyle.DANGER)

			async def callback(self, ctx: ViewContext) -> None:
				def get_next_item(sequence: list, previous):
					index = sequence.index(previous)
					return sequence[index + 1] if index + 1 < len(sequence) else None

				next_label = get_next_item(self.messages, self.label)

				if next_label is None:
					await ctx.respond_with_modal(
						DeleteProfileConfirmationModal(
							ctx.author.username,
							self.profile_id,
							view_ctx=ctx,
						),
					)

				self.label = next_label or self.messages[0]

				if next_label is None:
					await self.menu.on_timeout()
					self.menu.stop()
				else:
					await self.menu.update_message()

		class ProfileScreen(Screen):
			prev_ctx: arc.GatewayContext
			profile_id: ProfileID

			def __init__(self, menu: Menu, *, ctx: arc.GatewayContext | miru.ViewContext, profile_id: ProfileID) -> None:
				super().__init__(menu)

				self.prev_ctx = ctx
				self.profile_id = profile_id

				with UserDB(self.prev_ctx.author.id) as user:
					already_selected = user.is_selected(profile_id)

				self.add_item(PopScreenButton())
				self.add_item(SwitchToProfileButton(profile_id, already_selected=already_selected))
				self.add_item(DeleteProfileButton(profile_id))

			async def build_content(self) -> ScreenContent:
				with UserDB(self.prev_ctx.author.id) as user:
					try:
						prof = user.get_profile_by_id(self.profile_id)
					except KeyError:
						self.clear_items()

						return ScreenContent(
							content=f"**Whoops, it looks like this profile is missing!** If you didnt *just* delete this profile, something went wrong, if this issue persists or it appears your profile/data is gone or you just want to report this as a bug, contact the bot's developer: {S.AUTHOR.get_developer_contact_info()}",
							user_mentions=True,
						)

					return ScreenContent(
						embed=hikari.Embed(
							title=None,
							description=None,
							color=S.COLOR.PRIMARY,
						)
						.set_author(
							name=self.prev_ctx.author.display_name,
							icon=self.prev_ctx.author.make_avatar_url() or self.prev_ctx.author.default_avatar_url,
						)
						.add_field(
							name="Profile info",
							value=f"""
{prof.make_md_ident_name()}
"""[1:-1],
							inline=True,
						),
					)

	if True:  # NewProfileScreen

		@enforce_owned_callback
		class CreateProfileButton(OwnedScreenButton):
			def __init__(self) -> None:
				super().__init__(label="Create profile!", style=hikari.ButtonStyle.SUCCESS)

			async def callback(self, ctx: ViewContext) -> None:
				with UserDB(ctx.author.id) as user:
					try:
						new_profile = user.create_profile(owner=ctx.author)
					except ValueError:  # all profile IDs depleted somehow
						await ctx.respond(f"{S.NO} You have reached the maximum amount of profiles.", flags=hikari.MessageFlag.EPHEMERAL)
						return

					user.select_profile(new_profile)

				self.menu.stop()
				await self.menu.on_timeout()
				await ctx.respond(f"{S.YES} **Successfuly created a new profile and switched to it!**")

		class NewProfileScreen(Screen):
			prev_ctx: arc.GatewayContext

			def __init__(self, menu: Menu, *, ctx: arc.GatewayContext) -> None:
				super().__init__(menu)

				self.prev_ctx = ctx

				self.add_item(PopScreenButton())
				self.add_item(CreateProfileButton())

			async def build_content(self) -> ScreenContent:
				return ScreenContent(
					embed=hikari.Embed(
						title=None,
						description=f"""
Each profile contains its own reminders, settings, cooldowns, and everything in between. Think of them like files for a video game. **Your current data will not be lost**.

✅ **Note: Data *can* be transferred between profiles.** There is no cooldown for creating or switching profiles, but there's a (high) limit for amount of them.

Check out [**Zoo**](https://gdcolon.com/zoo/) (<@1008563327380766812>) made by [**Colon**](https://gdcolon.com) {S.EMOJI.fluff} from which i umm.. *took much inspiration* for this profile system. It's really cool!
"""[1:-1],
						color=S.COLOR.PRIMARY,
					).set_author(
						name="Start a new profile?",
						icon=self.prev_ctx.author.make_avatar_url() or self.prev_ctx.author.default_avatar_url,
					),
				)


class ProfilesSlashCmdMenu(OwnedMenu, DisableItemsOnTimeoutMenu, MultipleStartingScreenStackMenu): ...


@ACL.include
@arc.slash_command(**LANG.get_arc_command("/.profiles"))
async def cmd_profiles(
	ctx: arc.GatewayContext,
	profile_str: arc.Option[str | None, arc.StrParams(**LANG.get_arc_command("/.profiles:profile"), autocomplete_with=_autocomplete_profile)] = None,
) -> None:
	menu = ProfilesSlashCmdMenu(timeout=S.MIRU_TIMEOUT, owner=ctx.author)

	stack = [ProfilesListScreen(menu, ctx=ctx)]

	if profile_str is not None:
		stack.append(
			ProfileScreen(
				menu,
				ctx=ctx,
				profile_id=ProfileID.try_from_str(profile_str),
			)
		)

	builder = await menu.build_response_async(MCL, *stack)

	inter = await ctx.respond_with_builder(builder)

	MCL.start_view(menu, bind_to=await inter.retrieve_message())
