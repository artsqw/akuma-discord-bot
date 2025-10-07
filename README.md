## Akuma DiscordBot

This was my **first experience developing this type of bot**. During the process, I practiced working with **cogs**, **databases**, and applied my knowledge of **Python OOP**.

### Features:

- ⚠️ Warning system
- ⭐ Point system
- 💬 Comment system
- 🚫 Blacklist system
- 🔐 Access rights system

The bot is built using the [**Disnake.py**](https://github.com/DisnakeDev/disnake) library.

---

### Additional Details:

- 📄 **Pagination system** — all lists (warnings, points, etc.) have pagination when overflowing
- 🗄️ **Local database** — all data is stored in local **aiosqlite** databases to avoid database lock errors
- 🧩 **Modular design** — all bot functionalities are divided into separate files (**cogs**) for better organization and maintainability

### How to launch a bot?

1. To launch the bot, you will need to create your bot on the [official Discord developers website.](https://discord.com/developers/). [A guide on how to get a token and copy it](https://www.writebots.com/discord-bot-token/)
2. In the file located in the root of the repository (mine.py), find the line bot.run("TOKEN"), and instead of the expression TOKEN, insert your token (keeping the brackets)

⚠️ It's also worth noting that Discord doesn't register slash commands immediately, and this can take a long time. To work around this limitation, add the test_guilds argument to the commands.Bot function and specify the required values.
[For more information on the meaning of this argument when initializing a bot, see the Disnake documentation itself.](https://docs.disnake.dev/en/latest/ext/commands/slash_commands.html)

### Commands:

# Blacklist:
/gbl - Issue blacklist
/cbl - Check for a blacklist (or information about it)
/check_nickname - Check availability by nickname
-# In general, it was planned to add a user portfolio to this function, but the development for certain purposes was completed and never added.
/rbl - Remove blacklist

# Commentaries:
/comment - Add a comment to a user profile
/rcomment - Delete user comment
/gcomment - Check if a user has comments

# Permissions:
/access - Grant/remove access to a user
/list_access - Check the list of people with rights

# Points:
/point - Give/remove points to a user
/points - Check availability of points

# Warnings:
/warn - Issue/remove warning to user
/warns - Check for warnings

---

> This project was originally developed in **2024**.  
> Currently, all comments are written in English for better readability.
