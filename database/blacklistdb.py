import aiosqlite
import asyncio

class BlackListDB:
    def __init__(self):
        self.name = 'dbs/blacklist.db'
        self.connection = None


    async def create(self):
        self.connection = await aiosqlite.connect(self.name)
        await self.create_table()


    async def create_table(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                user INTEGER,
                nicknames TEXT,
                moderator INTEGER,
                reason INTEGER,
                type TEXT,
                type_text TEXT,
                date TEXT,
                PRIMARY KEY (user, moderator, date)
            )
            """)
            await self.connection.commit()

    async def add_to_blacklist(self, user, nicknames, moderator, type, type_text, reason):
        if await self.check_blacklist_type(user, type):
            return f"Пользователь {user.mention} уже имеет {type_text}."

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            INSERT INTO blacklist (user, nicknames, moderator, type, type_text, reason, date) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user.id, nicknames, moderator.id, type, type_text, reason, now))
            await self.connection.commit()

    async def get_blacklist(self, user):
        bl_info = ""

        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            SELECT type, type_text, reason, date, moderator, nicknames FROM blacklist WHERE user = ?
            """, (user.id,))
            data = await cursor.fetchall()

            if data:
                for type, type_text, reason, date, moderator, nicknames in data:
                    bl_info += f"**Никнейм(ы):** {nicknames}\n**Выдал:** <@{moderator}>\n**Тип:** {type_text}\n**Причина:** {reason}\n**Дата:** {date}\n\n"
                return bl_info
            else:
                return "У данного пользователя черных списков не обнаружено"


    async def check_blacklist_type(self, user, check_type):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            SELECT type FROM blacklist WHERE user = ? AND type = ?
            """, (user.id, check_type))
            result = await cursor.fetchone()
            return result is not None

    async def search_by_nickname(self, nickname):
        async with self.connection.cursor() as cursor:
            query = """
            SELECT user, nicknames, moderator, type_text, reason, date FROM blacklist WHERE 
            nicknames LIKE ? OR nicknames LIKE ? OR nicknames LIKE ? OR nicknames LIKE ?
            """
            like_pattern = f'%{nickname}%'
            like_pattern_start = f'{nickname},%'
            like_pattern_middle = f'%,{nickname},%'
            like_pattern_end = f'%,{nickname}'

            await cursor.execute(query, (like_pattern, like_pattern_start, like_pattern_middle, like_pattern_end))
            results = await cursor.fetchall()

            if results:
                bl_info = ""
                for row in results:
                    user_id, nicknames, moderator_id, type_text, reason, date = row

                    bl_info += (f"**Никнейм(ы):** {nicknames}\n**Выдал:** <@{moderator_id}>\n**Тип:** {type_text}\n"
                                f"**Причина:** {reason}\n**Дата:** {date}\n**Пользователь (кому выдано):** <@{user_id}>\n")

                return bl_info
            else:
                return "Ник не найден в черном списке."

    async def remove_from_blacklist(self, user, check_type):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            DELETE FROM blacklist WHERE user = ? AND type = ?
            """, (user.id, check_type))
            await self.connection.commit()

            if cursor.rowcount == 0:
                return f"Пользователь {user.mention} не найден в указанном черном списке."
            return None


blacklist_db = BlackListDB()
asyncio.run(blacklist_db.create())