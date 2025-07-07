import disnake
from disnake.ext import commands
from datetime import datetime
from Akuma.database import points_db


class Buttons(disnake.ui.View):
    def __init__(self, embeds, interaction):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.interaction = interaction
        self.offset = 0


        for emb in self.embeds:
            emb.set_footer(text=f'Страница {self.embeds.index(emb) + 1}/{len(self.embeds)}')


    async def update_button(self):
        is_first_page = self.offset == 0
        is_last_page = self.offset == len(self.embeds) - 1

        self.back.disabled = is_first_page
        self.forward.disabled = is_last_page


    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if self.interaction.author.id != interaction.user.id:
            embed = disnake.Embed(color=0xff0000).set_author(name="Ошибка")
            embed.description = (f"{interaction.author.mention}, Вы **не** можете использовать эту кнопку")
            embed.set_thumbnail(url=interaction.author.display_avatar)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        return True


    @disnake.ui.button(label='Назад', style=disnake.ButtonStyle.grey)
    async def back(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.offset > 0:
            self.offset -= 1
            await self.update_button()
            await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)


    @disnake.ui.button(label='Вперед', style=disnake.ButtonStyle.grey)
    async def forward(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.offset < len(self.embeds) - 1:
            self.offset += 1
            await self.update_button()
            await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)


class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Issue points to a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Выдать баллы пользователю")
    async def point(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.param(name="пользователь"),
                   amount: int = commands.param(name="количество"), reason: str = commands.param(name="причина")):
        moderator = inter.author.id

        await points_db.add_point(user, moderator, amount, reason)

        points_count = await points_db.get_points_count(user)

        embed = disnake.Embed(
            title="Баллы",
            description=f"Пользователь {user.mention} получил баллы.",
            color=disnake.Color.green()
        )
        embed.add_field(name="Причина", value=reason)
        embed.add_field(name="Модератор", value=f"<@{moderator}>")
        embed.add_field(name="Количество баллов", value=amount)

        await inter.response.send_message(embed=embed, ephemeral=True)


    # See the points history of a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Посмотреть историю баллов пользователя")
    async def points(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.param(name="пользователь")):
        points = await points_db.get_points(user)

        if not points:
            embed = disnake.Embed(
                title="История баллов",
                description=f"У {user.mention} нет баллов.",
                color=disnake.Color.green()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"История баллов пользователя {user.name}",
            color=disnake.Color.green()
        )

        embeds = await points_db.get_embeds(inter, user)
        if len(embeds) == 0:
            return await inter.response.send_message(
                f"У {user.mention} отсутствуют баллы",
                ephemeral=True,
            )
        view = Buttons(embeds, inter)
        await view.update_button()
        await inter.response.send_message(embed=embeds[0], view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(Points(bot))
