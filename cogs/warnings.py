import disnake
from disnake.ext import commands
from Akuma.database import warnings_db


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


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Issue a warning to a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Выдать предупреждение пользователю")
    async def warn(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.param(name="пользователь"),
                   amount: int = commands.param(name="количество"), reason: str = commands.param(name="причина")):
        moderator = inter.author.id

        await warnings_db.add_warning(user, moderator, amount, reason)

        warning_count = await warnings_db.get_warning_count(user)

        embed = disnake.Embed(
            title="Предупреждение",
            description=f"Пользователь {user.mention} получил предупреждение.",
            color=disnake.Color.red()
        )
        embed.add_field(name="Причина", value=reason)
        embed.add_field(name="Модератор", value=f"<@{moderator}>")
        embed.add_field(name="Количество предупреждений", value=amount)

        await inter.response.send_message(embed=embed, ephemeral=True)


    # View warnings of a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Посмотреть историю предупреждений пользователя")
    async def warns(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.param(name="пользователь")):
        warnings = await warnings_db.get_warnings(user)

        if not warnings:
            embed = disnake.Embed(
                title="История предупреждений",
                description=f"У {user.mention} нет предупреждений.",
                color=disnake.Color.green()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"История предупреждений пользователя {user.name}",
            color=disnake.Color.red()
        )

        embeds = await warnings_db.get_embeds(inter, user)
        if len(embeds) == 0:
            return await inter.response.send_message(
                f"У {user.mention} отсутствуют предупреждения",
                ephemeral=True,
            )
        view = Buttons(embeds, inter)
        await view.update_button()
        await inter.response.send_message(embed=embeds[0], view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(Warnings(bot))
