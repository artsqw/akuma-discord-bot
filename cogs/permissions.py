import disnake
from disnake.ext import commands
from Akuma.database.permissionsdb import permissions_db


class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Access levels
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Управлять правами пользователя")
    async def access(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.Param(name="пользователь"),
                     level: int = commands.Param(name="уровень-прав", choices=[
                         disnake.OptionChoice(name="Удалить права", value=0),
                         disnake.OptionChoice(name="Начальный уровень", value=1),
                         disnake.OptionChoice(name="Повышенный уровень", value=2),
                         disnake.OptionChoice(name="Полный доступ", value=3)
                     ])):
        required_level = 3
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions and user.id != #id of the bot owner:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        error_message = await permissions_db.set_access(user, level)

        if error_message:
            embed = disnake.Embed(
                title="Ошибка",
                description=error_message,
                color=disnake.Color.red()
            )
        else:
            embed = disnake.Embed(
                title="Успех",
                description=f"Права для пользователя {user.mention} установлены на уровень {level}.",
                color=disnake.Color.green()
            )

        await inter.response.send_message(embed=embed, ephemeral=True)


    # List all users and their access levels
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Показать список пользователей и их уровни прав")
    async def list_access(self, inter: disnake.ApplicationCommandInteraction):
        required_level = 1
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        permissions = await permissions_db.get_all_permissions()

        if not permissions:
            embed = disnake.Embed(
                title="Нет пользователей",
                description="Нет пользователей с правами в базе данных.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title="Список пользователей с правами",
            color=disnake.Color.blue()
        )

        # Categorize users by their access levels
        full_access = []
        elevated_access = []
        initial_access = []

        # Iterate through permissions and categorize users
        for user_id, level in permissions:
            user = await self.bot.fetch_user(user_id)
            if level == 3:
                full_access.append(f"<@{user.id}>")
            elif level == 2:
                elevated_access.append(f"<@{user.id}>")
            elif level == 1:
                initial_access.append(f"<@{user.id}>")

        if full_access:
            embed.add_field(name="Полный доступ:", value="\n".join(full_access), inline=False)
        if elevated_access:
            embed.add_field(name="Повышенный доступ:", value="\n".join(elevated_access), inline=False)
        if initial_access:
            embed.add_field(name="Начальный доступ:", value="\n".join(initial_access), inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Permissions(bot))
