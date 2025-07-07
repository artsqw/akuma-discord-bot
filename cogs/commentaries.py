import disnake
from disnake.ext import commands
from datetime import datetime


from Akuma.database import commentaries_db
from Akuma.database import permissions_db


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


class Commentaries(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Leave a comment for a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Оставить комментарий пользователю")
    async def comment(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.Param(name='пользователь'),
                      commentary: str = commands.Param(name='содержание')):
        required_level = 2
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return

        date = datetime.now()
        formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")

        await commentaries_db.add_comment(user, inter.author.id, commentary, formatted_date)

        comment = disnake.Embed(
            title="Добавление комментария",
            description="",
            color=disnake.Colour.green(),
        )
        comment.add_field(name="Кому выдан", value=f"{user.mention}", inline=False)
        comment.add_field(name="Содержание комментария", value=f"- {commentary}", inline=False)
        comment.set_thumbnail(url=user.avatar)
        await inter.response.send_message(embed=comment, ephemeral=True)


    # Delete a comment for a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Удаляет комментарий пользователю")
    async def rcomment(self, inter: disnake.ApplicationCommandInteraction, id: int = commands.Param(name='id-комментария')):
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
        exists = await commentaries_db.record_exists(id)
        if exists:
            commentary = await commentaries_db.get_comments_where_id(id)
            comments = disnake.Embed(
                title="Удаление комментария",
                description="",
                color=disnake.Colour.red(),
            )
            comments.add_field(name="ID комментария", value=f"{id}", inline=False)
            comments.add_field(name="Содержание комментария", value=f"- {commentary}", inline=False)
            await commentaries_db.del_comment(id)
            await inter.response.send_message(embed=comments, ephemeral=True)
        else:
            await inter.response.send_message("Такой ID не существует!", ephemeral=True)


    # Edit a comment for a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Обновляет комментарий пользователю")
    async def ecomment(self, inter: disnake.ApplicationCommandInteraction, id: int = commands.Param(name='id-комментария'),
                       new_commentary: str = commands.Param(name='новый-комментарий')):
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
        await commentaries_db.edit_comment(id, new_commentary)
        await inter.response.send_message("Комментарий обновлен!", ephemeral=True)


    # Get comments of a user
    @commands.default_member_permissions(administrator=True)
    @commands.slash_command(description="Получает комментарии пользователя")
    async def gcomment(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = commands.Param(name='пользователь')):
        required_level = 2
        has_permissions = await permissions_db.check_permissions(inter.author, required_level)

        if not has_permissions:
            embed = disnake.Embed(
                title="Ошибка прав",
                description="У вас недостаточно прав для выполнения этой команды.",
                color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        embeds = await commentaries_db.get_embeds(inter, user)
        if len(embeds) == 0:
            return await inter.response.send_message(
                f"У {user.mention} отсутствуют комментарии",
                ephemeral=True,
            )
        view = Buttons(embeds, inter)
        await view.update_button()
        await inter.response.send_message(embed=embeds[0], view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(Commentaries(bot))
