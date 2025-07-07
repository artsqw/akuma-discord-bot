import aiosqlite
import asyncio
import disnake

class Permissionsdb:
    def __init__(self):
        self.name = 'dbs/permissions.db'
        self.connection = None


    async def create(self):
        self.connection = await aiosqlite.connect(self.name)
        await self.create_table()


    async def create_table(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                user INTEGER,
                lvl INTEGER
            )
            """)
            await self.connection.commit()


    async def set_access(self, user, level):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT lvl FROM permissions WHERE user = ?", (user.id,)
            )
            current_level = await cursor.fetchone()

            if current_level:
                current_level = current_level[0]
                if current_level == level:
                    return f"У пользователя уже есть права уровня {current_level}."

            if level == 0:
                await cursor.execute("DELETE FROM permissions WHERE user = ?", (user.id,))
            else:
                await cursor.execute(
                    "SELECT * FROM permissions WHERE user = ?", (user.id,)
                )
                existing_record = await cursor.fetchone()
                if existing_record:
                    await cursor.execute(
                        "UPDATE permissions SET lvl = ? WHERE user = ?",
                        (level, user.id)
                    )
                else:
                    await cursor.execute(
                        "INSERT INTO permissions (user, lvl) VALUES (?, ?)",
                        (user.id, level)
                    )

            await self.connection.commit()


    async def get_access(self, user):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT lvl FROM permissions WHERE user = ?", (user.id,)
            )
            result = await cursor.fetchone()
            if result:
                return result[0]
            return None


    async def get_all_permissions(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT user, lvl FROM permissions")
            return await cursor.fetchall()


    async def remove_permission(self, user):
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM permissions WHERE user = ?", (user.id,))
            await self.connection.commit()


    async def check_permissions(self, user, required_level):
        async with permissions_db.connection.cursor() as cursor:
            await cursor.execute("SELECT lvl FROM permissions WHERE user = ?", (user.id,))
            result = await cursor.fetchone()

        if not result or result[0] < required_level:
            return False
        return True


permissions_db = Permissionsdb()
asyncio.run(permissions_db.create())
