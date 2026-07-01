# Suggests Bot - Developer Guide & Architecture (AGENT.md)

This document provides a comprehensive overview of the **Suggests Bot** codebase, database schema, and deployment workflows. It is designed to allow new AI agents and developers to quickly understand the project without needing to explore modules from scratch in every session.

---

## 1. Project Overview

The **Suggests Bot** is a Telegram-based post-suggestion system. It consists of:
1. **A Master (Main) Bot**: Users interact with this bot to purchase subscriptions/premium plans, generate and manage their own suggestions bots.
2. **Dynamic Suggestions Bots**: Independent, dynamically-added bots managed under a single webhook endpoint. Suggesters use them to submit posts/media, and channel administrators use them to approve, edit, or publish suggestions to their linked Telegram channels.

---

## 2. Architecture & Directory Structure

The project is built on `aiogram 3.x` and `aiohttp`, utilizing webhooks to handle multiple bots concurrently.

### Entrypoint & Webhook Router (`main.py`)
- Configures two dispatchers:
  - `main_dispatcher`: Routes updates for the Master Bot (webhook: `/suggests/main`).
  - `other_bots_dispatcher`: Dynamically routes updates for user-managed bots (webhook: `/suggests/bot/{bot_token}`) via aiogram's `TokenBasedRequestHandler`.
- Runs background tasks via `AsyncIOScheduler`:
  - `db_subscriptions_checker` (Daily): Cleans up expired subscriptions.
  - `pre_render_platform_charts` (Hourly): Pre-renders activity graphs using `matplotlib`.

### Directory Tree & Modules
- **`handlers/`**:
  - `main_bot/`: Handles interactions with the Master Bot.
    - `users/`: Setup of user bots, buying/viewing subscriptions, checking bot states.
    - `premium/`: Premium configuration (e.g., custom post formatting, multi-administrator access).
    - `creators/`: Master Admin/Creator dashboard, system broadcasts, viewing income.
  - `other_bots/`: Handles interactions with dynamic suggestions bots.
    - `admins/`: Banning users, cleaning queues, approving/editing suggestions.
    - `users/`: Submitting suggestions (text, photos, media groups).
    - `chat_member.py`: Handles `my_chat_member` updates (adding/deleting bots from Telegram channels).
- **`database/`**:
  - Encapsulates database tables and custom SQL queries using `SQLAlchemy` (Async session).
  - Exposed via `DataBaseApi` in `data/config.py` under the global variable `db`.
- **`filters/`**:
  - Custom filters for routing updates: `is_admin.py`, `is_user.py`, `is_sub.py`, `admins_query.py`.
- **`keyboards/`**:
  - Keyboards and inline reply buttons for different menus.
- **`payments/`**:
  - Integration with payment systems: `aaio.py`, `cryptobot.py`, `plat.py`.
- **`utils/`**:
  - Utilities such as `album_collector.py` (grouping media groups), `graphic_maker.py` (pre-rendering charts), and notifier scripts.

---

## 3. Database Schema & Models (`database/model.py`)

The application uses **PostgreSQL**. The database schema contains the following main models:

### Admin (`admin` table)
Represents administrators who manage suggestions bots.
- `id` (BigInteger, Primary Key) - Telegram User ID.
- `language_code` (String(2))
- `name` (String(255))
- `is_active` (Boolean)
- `label` (String(255))

### Bot (`bot` table)
Represents dynamic suggestion bots created by administrators.
- `id` (BigInteger, Primary Key) - Telegram Bot ID.
- `name` (String(255))
- `url` (String(255))
- `token` (String(255), Unique)
- `banlist` (ARRAY of BigInteger) - Banned suggesters.
- `post_formatting` (Text) - Format string.
- `is_active` (Boolean)
- `is_premium` (Boolean)
- `creator_id` (BigInteger, ForeignKey to `admin.id`)
- **Relationships**:
  - `admins`: Many-to-many relationship with `Admin` table via `admin_bot_association` junction table.

### Channels (`channels` table)
Linked publishing destinations for suggestion bots.
- `primary_key` (BigInteger, Primary Key)
- `id` (BigInteger) - Telegram Channel ID (Note: can be mapped to multiple bots, so it is not unique).
- `name` (String(255))
- `bot_id` (BigInteger, ForeignKey to `bot.id`)

### SuggestedMessage (`suggested_message` table)
Draft posts submitted by users.
- `primary_key` (BigInteger, Primary Key)
- `id` (BigInteger) - Telegram Message ID.
- `chat_id` (BigInteger) - Origin chat ID.
- `media_group_id` (String(255)) - Groups photos/videos in the same post.
- `sender_id` (BigInteger, ForeignKey to `sender.id`)
- `bot_id` (BigInteger, ForeignKey to `bot.id`)
- `html_text` (Text)
- `message_data` (JSON) - Complete raw message structure.

### Subscription (`subscription` table)
Premium plans purchased by administrators.
- `id` (BigInteger, Primary Key)
- `admin_id` (BigInteger, ForeignKey to `admin.id`)
- `start_date` (DateTime with Timezone)
- `end_date` (DateTime with Timezone)
- `plan` (String(255))

---

## 4. Development & Deployment Workflow

### Local Development & Verification
1. **LSP Integration**: Work with the codebase locally using any Python LSP.
2. **Syntax Compilation Check**: Before pushing or testing, verify the python syntax of modified files by running:
   ```bash
   python3 -m py_compile <file_path_1> <file_path_2>
   ```

### Push-to-Deploy Cycle
1. **Stage & Commit**: Stage only the files containing verified fixes/features (avoid staging local test configurations like commented out proxies in `main.py`):
   ```bash
   git add handlers/other_bots/chat_member.py database/channel.py
   git commit -m "Commit description"
   ```
2. **Push to GitHub**:
   ```bash
   git push
   ```

### Production Environment (`timeweb` Server)
1. **SSH Connection**:
   - Host IP: `45.95.234.203` (registered alias: `timeweb`).
   - Log in as `root`.
2. **Repository Directory**: `/root/suggests_bot`
3. **Pulling Changes**:
   ```bash
   cd /root/suggests_bot
   git pull
   ```
4. **PostgreSQL Database**:
   - Connection URL: `postgresql+asyncpg://inno:root@localhost/suggests_db`
   - Password: `root`
   - Access DB CLI directly:
     ```bash
     PGPASSWORD=root psql -U inno -d suggests_db -h localhost
     ```
5. **Managing Bot Daemon**:
   - The bot runs as a systemd service: `suggests-bot.service`.
   - **Restart service**:
     ```bash
     systemctl restart suggests-bot.service
     ```
   - **Check logs (systemd journal)**:
     ```bash
     journalctl -u suggests-bot.service -n 50 --no-pager
     ```
     Or tail logs in real-time:
     ```bash
     journalctl -u suggests-bot.service -f
     ```
