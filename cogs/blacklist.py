import disnake
from disnake.ext import commands

from Akuma.database import blacklist_db
from Akuma.database.permissionsdb import permissions_db


class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    blacklists = {
        1: {'title': 'ЧС проекта'},
        2: {'title': 'ЧС администрации'},
    }

    # Give a blacklist to a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Выдать черный список пользователю")
    async def gbl(self, inter: disnake.ApplicationCommandInteraction,
                  user: disnake.Member = commands.Param(name="пользователь"),
                  type: int = commands.Param(name="тип-черного-списка", choices=[
                      disnake.OptionChoice(name="ЧС проекта", value=1),
                      disnake.OptionChoice(name="ЧС администрации", value=2)
                  ]),
                  reason: str = commands.Param(name="причина-занесения"),
                  nicknames: str = commands.Param(name="никнеймы-игрока")):
        required_level = 3
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        # Get the type text based on the type of blacklist
        type_text = self.blacklists.get(type, {}).get('title', "Неизвестный тип")

        # Returning an error message if error occurs
        error_message = await blacklist_db.add_to_blacklist(user, nicknames, inter.author, type, type_text, reason)

        if error_message:
            embed = disnake.Embed(
                title="Ошибка",
                description=error_message,
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(
                title="Выдача черного списка",
                description=f"Пользователю {user.mention} ({nicknames}) был выдан черный список",
                color=disnake.Color.red(),
            )
            embed.add_field(name="Выдал", value=inter.author.mention)
            embed.add_field(name="Тип черного списка", value=type_text)
            embed.add_field(name="Причина выдачи", value=reason)
            embed.set_thumbnail(url=user.display_avatar)
            await inter.response.send_message(embed=embed, ephemeral=True)

        if type == 1:
            await blacklist_db.add_to_blacklist(user, nicknames, inter.author, 1, "ЧС проекта", reason)
        elif type == 2:
            await blacklist_db.add_to_blacklist(user, nicknames, inter.author, 2, "ЧС администрации", reason)


    # Check if a user is in the blacklist
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Проверить пользователя на наличие черного списка")
    async def cbl(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.Param(name="пользователь")):
        required_level = 3
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            gbl_info = await blacklist_db.get_blacklist(user)
            embed = disnake.Embed(
                title="Информация по наличию черного списка",
                description=f"{gbl_info}",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(url=user.display_avatar)
            await inter.response.send_message(embed=embed, ephemeral=True)


    # Check if a nickname is in the blacklist
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Проверка на наличие черного списка через никнейм")
    async def check_nickname(self, inter: disnake.ApplicationCommandInteraction, nickname: str = commands.Param(name="никнейм")):
        required_level = 3
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            gbl_info = await blacklist_db.search_by_nickname(nickname)
            embed = disnake.Embed(
                title="Информация по наличию черного списка",
                description=f"{gbl_info}",
                color=disnake.Color.red(),
            )
            await inter.response.send_message(embed=embed, ephemeral=True)


    # Remove a user from the blacklist
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Удалить пользователя из черного списка")
    async def rbl(self, inter: disnake.ApplicationCommandInteraction,
                                    user: disnake.Member = commands.Param(name="пользователь"),
                                    type: int = commands.Param(name="тип-черного-списка", choices=[
                                        disnake.OptionChoice(name="ЧС проекта", value=1),
                                        disnake.OptionChoice(name="ЧС администрации", value=2)
                                    ])):
        required_level = 3
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        error_message = await blacklist_db.remove_from_blacklist(user, type)

        if error_message:
            embed = disnake.Embed(
                title="Ошибка",
                description=error_message,
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            type_text = self.blacklists.get(type, {}).get('title', "Неизвестный тип")
            embed = disnake.Embed(
                title="Удаление из черного списка",
                description=f"Пользователь {user.mention} был удален из списка: {type_text}.",
                color=disnake.Color.green()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Blacklist(bot))
