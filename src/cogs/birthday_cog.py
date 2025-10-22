from __future__ import annotations

from datetime import date

from discord import app_commands
from discord import Interaction
from discord import Member
from discord.ext import commands

from src.database import database_utils
from src.database.database_utils import get_birthday_for_user
from src.database.database_utils import get_birthdays_today
from src.models.schemas import BirthdaySchema
from src.service.logger_service import logger
from src.service.util_service import Category


class Birthday(commands.Cog):
    def __init__(self, client):
        self.client = client

    def _save_birthday(self, target_id: int, bdate: date):
        """Shared helper to persist a birthday for a user id."""
        database_utils.ensure_user_exists(target_id)
        birthday_entry = BirthdaySchema(user_id=target_id, birthday=bdate)
        database_utils.add(birthday_entry)
        logger.info(f"Saved birthday for {target_id}: {bdate}")
        return birthday_entry

    @commands.command(
        name="birthday",
        help="Set your birthday in the format DD-MM-YYYY",
        usage=Category.settings,
    )
    async def birthday(self, ctx, date_str: str):
        """Set the user's birthday."""
        try:
            # Validate the date format
            day, month, year = map(int, date_str.split("-"))
            # store as a real date object so SQLAlchemy/SQLite accepts it
            birthday_date = date(year, month, day)
            # Ensure the user exists in users table (foreign key) then persist birthday
            database_utils.ensure_user_exists(
                ctx.author.id, getattr(ctx.author, "name", None)
            )
            # Create a BirthdaySchema instance and persist
            birthday_entry = BirthdaySchema(
                user_id=ctx.author.id, birthday=birthday_date
            )
            database_utils.add(birthday_entry)
            logger.info(f"Setting birthday for user {ctx.author.id} to {birthday_date}")

        except ValueError:
            await ctx.send("Invalid date format. Please use DD-MM-YYYY.")
            return

        await ctx.send(f"Your birthday has been set to {date_str}.")

    @commands.command(
        name="birthdays_today",
        help="Get a list of users with birthdays today",
        usage=Category.settings,
    )
    async def birthdays_today(self, ctx):
        """Get a list of users with birthdays today."""
        await ctx.send(get_birthdays_today())

    # Slash command wrapper for get_birthday
    @app_commands.command(name="get_birthday")
    @app_commands.describe(
        user="User to look up (mention or id). Omit to see your own birthday"
    )
    async def get_birthday_slash(self, interaction: Interaction, user: str = None):
        # permission-wise this mirrors the prefix command (any user can query)
        # Determine target id
        if user is None:
            target_id = interaction.user.id
        else:
            import re

            m = re.search(r"(\d{17,20})", user)
            if not m:
                await interaction.response.send_message(
                    "Could not parse user id from input. Please mention the user or pass their numeric id.",
                    ephemeral=True,
                )
                return
            target_id = int(m.group(1))

        birthday = get_birthday_for_user(target_id)
        if birthday:
            if hasattr(birthday, "strftime"):
                await interaction.response.send_message(
                    f"Birthday for <@{target_id}> is {birthday.strftime('%d-%m-%Y')}"
                )
            else:
                await interaction.response.send_message(
                    f"Birthday for <@{target_id}> is {birthday}"
                )
        else:
            await interaction.response.send_message(
                f"No birthday found for <@{target_id}>"
            )

    # Slash command wrapper for add_birthday (admin only)
    @app_commands.command(name="add_birthday")
    @app_commands.describe(
        user="User to set birthday for (mention or id)",
        date_str="Birthday in DD-MM-YYYY",
    )
    async def add_birthday_slash(
        self, interaction: Interaction, user: str, date_str: str
    ):
        # check admin perms: resolve a Guild Member object if possible
        member = None
        if isinstance(interaction.user, Member):
            member = interaction.user
        elif interaction.guild is not None:
            # try cache first
            member = interaction.guild.get_member(interaction.user.id)
            # if not cached, try fetching (may raise in some test environments)
            if member is None:
                try:
                    member = await interaction.guild.fetch_member(interaction.user.id)
                except Exception:
                    member = None

        if member is None or not member.guild_permissions.administrator:
            await interaction.response.send_message(
                "You need Administrator permission to run this command.", ephemeral=True
            )
            return

        import re

        m = re.search(r"(\d{17,20})", user)
        if not m:
            await interaction.response.send_message(
                "Could not parse user id from input. Please mention the user or pass their numeric id.",
                ephemeral=True,
            )
            return
        target_id = int(m.group(1))

        try:
            day, month, year = map(int, date_str.split("-"))
            bdate = date(year, month, day)
        except ValueError:
            await interaction.response.send_message(
                "Invalid date format. Please use DD-MM-YYYY.", ephemeral=True
            )
            return

        self._save_birthday(target_id, bdate)
        await interaction.response.send_message(
            f"Set birthday for <@{target_id}> to {date_str}."
        )

    @commands.command(
        name="get_birthday",
        help="Get a user's birthday. Usage: f!get_birthday @user or f!get_birthday <id>",
    )
    async def get_birthday(self, ctx, user: str = None):
        """Look up a user's birthday by mention or id. If omitted, returns the invoker's birthday."""
        # Determine target id: either the provided mention/id or the invoking user
        if user is None:
            target_id = ctx.author.id
        else:
            # Accept mention like <@123...> or raw id
            import re

            m = re.search(r"(\d{17,20})", user)
            if not m:
                await ctx.send(
                    "Could not parse user id from input. Please mention the user or pass their numeric id."
                )
                return
            target_id = int(m.group(1))

        birthday = get_birthday_for_user(target_id)
        if birthday:
            # birthday may be a date object; display as DD-MM-YYYY for clarity
            if hasattr(birthday, "strftime"):
                await ctx.send(
                    f"Birthday for <@{target_id}> is {birthday.strftime('%d-%m-%Y')}"
                )
            else:
                await ctx.send(f"Birthday for <@{target_id}> is {birthday}")
        else:
            await ctx.send(f"No birthday found for <@{target_id}>")

    @commands.command(
        name="add_birthday",
        help="Add/set a birthday for another user (admin only). Usage: f!add_birthday @user DD-MM-YYYY",
    )
    @commands.has_permissions(administrator=True)
    async def add_birthday(self, ctx, user: str, date_str: str):
        """Admin helper: set a birthday for another user by mention or id."""
        # parse user id from mention or raw id
        import re

        m = re.search(r"(\d{17,20})", user)
        if not m:
            await ctx.send(
                "Could not parse user id from input. Please mention the user or pass their numeric id."
            )
            return
        target_id = int(m.group(1))

        try:
            day, month, year = map(int, date_str.split("-"))
            bdate = date(year, month, day)
        except ValueError:
            await ctx.send("Invalid date format. Please use DD-MM-YYYY.")
            return

        # ensure user row exists and persist
        database_utils.ensure_user_exists(target_id)
        birthday_entry = BirthdaySchema(user_id=target_id, birthday=bdate)
        database_utils.add(birthday_entry)
        await ctx.send(f"Set birthday for <@{target_id}> to {date_str}.")

        birthday = get_birthday_for_user(target_id)
        if birthday:
            await ctx.send(f"Birthday for <@{target_id}> is {birthday}.")
        else:
            await ctx.send(f"No birthday found for <@{target_id}>.")


async def setup(client):
    await client.add_cog(Birthday(client))
