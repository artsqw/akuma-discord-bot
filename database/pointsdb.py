import aiosqlite
import asyncio
import disnake

class PointsDB:
    def __init__(self):
        self.name = 'dbs/points.db'
        self.connection = None


    async def create(self):
        self.connection = await aiosqlite.connect(self.name)
        await self.create_table()


    async def create_table(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS points (
                user INTEGER,
                moderator INTEGER,
                amount INTEGER,
                reason TEXT,
                date TEXT,
                PRIMARY KEY (user, moderator, date)
            )
            """)
            await self.connection.commit()


    async def add_point(self, user, moderator, amount, reason):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            INSERT INTO points (user, moderator, amount, reason, date) 
            VALUES (?, ?, ?, ?, ?)
            """, (user.id, moderator, amount, reason, now))
            await self.connection.commit()


    async def get_points(self, user):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            SELECT amount, reason, date, moderator FROM points WHERE user = ?
            """, (user.id,))
            return await cursor.fetchall()


    async def get_points_count(self, user):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            SELECT SUM(amount) FROM points WHERE user = ?
            """, (user.id,))
            result = await cursor.fetchone()
            return result[0] if result else 0


    async def get_embeds(self, interaction, user):
        points = await points_db.get_points(user)
        embeds = []
        n = 0
        loop_count = 0
        text = ""
        for point in points:
            amount, reason, date, moderator = point
            n += 1
            text += (f"> Дата: {date}\n> Причина: {reason}\n> Выдал: <@{moderator}>\n> Количество: {amount}\n\n")
            loop_count += 1
            if loop_count % 5 == 0 or loop_count - 1 == len(points) - 1:
                embed = disnake.Embed(title=f"История баллов: {user.name}",
                                      description=text, color=disnake.Colour.red())
                embed.set_thumbnail(url=user.display_avatar)
                total_amount = await self.get_points_count(user)
                embed.add_field(name="🌿 Общее количество баллов", value=f"{total_amount} баллов", inline=False)
                embeds.append(embed)
                text = ""
        return embeds


points_db = PointsDB()
asyncio.run(points_db.create())