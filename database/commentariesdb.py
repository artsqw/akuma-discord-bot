import aiosqlite
import asyncio
import disnake

class Commentariesdb:
    def __init__(self):
        self.name = 'dbs/commentaries.db'
        self.connection = None

    async def create(self):
        self.connection = await aiosqlite.connect(self.name)
        await self.create_table()


    async def create_table(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS commentaries (
                user INTEGER,
                commenter INTEGER,
                commentary TEXT,
                date INTEGER,
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
            """)
            await self.connection.commit()

    async def add_comment(self, user, commenter, comment, date):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO commentaries (user, commenter, commentary, date) VALUES (?, ?, ?, ?)",
                (user.id, commenter, comment, date)
            )
            await self.connection.commit()


    async def del_comment(self, id):
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM commentaries WHERE id = ?", (id,))
            await self.connection.commit()


    async def edit_comment(self, id, new_commentary):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE commentaries SET commentary = ? WHERE id = ?",
                (new_commentary, id)
            )
            await self.connection.commit()


    async def get_comments(self, user):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT date, commenter, commentary, id FROM commentaries WHERE user = ?", (user.id,)
            )
            return await cursor.fetchall()


    async def get_comments_where_id(self, id):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT commentary FROM commentaries WHERE id = ?", (id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None


    async def record_exists(self, id):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM commentaries WHERE id = ?)", (id,)
            )
            result = await cursor.fetchone()
            return result[0] == 1 if result else False

    async def get_embeds(self, interaction, user):
        data = await self.get_comments(user)
        embeds = []
        n = 0
        loop_count = 0
        text = ""
        for date, commenter, commentary, id in data:
            n += 1
            text += (f"> Дата: {date}\n> Оставил: <@{commenter}>\n> Содержание: {commentary}\n> ID: {id}\n\n")
            loop_count += 1
            if loop_count % 5 == 0 or loop_count - 1 == len(data) - 1:
                embed = disnake.Embed(title=f"Комментарии пользователя: {user.name}",
                                      description=text, color=0xFFA500)
                embed.set_thumbnail(url=user.display_avatar)
                embeds.append(embed)
                text = ""
        return embeds


commentaries_db = Commentariesdb()
asyncio.run(commentaries_db.create())