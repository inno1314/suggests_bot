from aiogram import types, F, Router, html
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, BigInteger, desc
from sqlalchemy.orm import selectinload
import time
import os
from datetime import datetime, timezone

from utils import (
    generate_view_count_chart,
    generate_revenue_chart,
    generate_activity_chart,
    chart_cache,
)
from database.model import Bot, Sender, Subscription, SuggestedMessage, Admin
from data.config import db

router = Router()


def get_stats_markup() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📈 Просмотры", callback_data="stats_view:ads"),
                types.InlineKeyboardButton(text="💰 Доходы", callback_data="stats_view:revenue"),
                types.InlineKeyboardButton(text="📊 Активность", callback_data="stats_view:activity"),
            ],
            [
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="to_admins_menu"),
            ],
        ]
    )


@router.callback_query(F.data == "show_incomes")
@router.callback_query(F.data.startswith("stats_view:"))
async def show_analytics(call: types.CallbackQuery, session: AsyncSession):
    data = call.data
    if data == "show_incomes":
        view = "ads"
    else:
        view = data.split(":")[1]

    # Check cache
    cache_key = f"platform_stats:{view}"
    cached_data = chart_cache.get(cache_key)

    if cached_data:
        photo, caption = cached_data
    else:
        pre_rendered_val = chart_cache.get(f"pre_rendered_val:{view}")

        if view == "ads":
            income_from_subs = await db.subscription_api.get_subscription_income(session)
            users_for_ad_mailing = await db.bot_api.get_all_users_for_ads(session)
            
            if pre_rendered_val is not None and os.path.exists("view_count_chart.png"):
                count = pre_rendered_val
                path = "view_count_chart.png"
            else:
                path, count = await generate_view_count_chart(session)
            photo = types.FSInputFile(path)

            # Get detailed premium subscriptions
            now_time = datetime.now(timezone.utc)
            active_subs_query = (
                select(Subscription)
                .where(Subscription.end_date > now_time)
                .options(selectinload(Subscription.admin).selectinload(Admin.bots))
            )
            active_subs = (await session.execute(active_subs_query)).scalars().all()
            
            limit_subs = 5
            subs_lines = []
            for sub in active_subs[:limit_subs]:
                admin_name = sub.admin.name or f"User {sub.admin_id}"
                bot_names = ", ".join(f"@{bot.url.split('/')[-1]}" if (bot.url and '/' in bot.url) else bot.name for bot in sub.admin.bots) or "нет"
                subs_lines.append(
                    f"  👤 <b>{admin_name}</b> (<code>{sub.admin_id}</code>)\n"
                    f"     └ Тариф: <code>{sub.plan}</code> | Боты: {bot_names}"
                )
            subs_text = "\n".join(subs_lines) if subs_lines else "  Нет активных подписок"
            if len(active_subs) > limit_subs:
                subs_text += f"\n  ... и еще <code>{len(active_subs) - limit_subs}</code> подписчиков."

            caption = (
                f"<b>📈 Просмотры рекламы и подписки</b>\n\n"
                f"💰 Месячный доход с подписок: <code>{income_from_subs}</code> руб.\n"
                f"👥 Рассылку увидят <code>{len(users_for_ad_mailing)}</code> пользователей\n"
                f"👁️ Показов рекламы в ответном сообщении (за последние 30 дней): <code>{count}</code>\n\n"
                f"🌟 <b>Премиум-подписчики ({len(active_subs)}):</b>\n{subs_text}"
            )

        elif view == "revenue":
            total_revenue = await db.payments_api.get_successful_payments_revenue(session)
            conv_rate = await db.payments_api.get_payment_conversion_rate(session)
            revenue_by_service = await db.payments_api.get_successful_payments_by_service(session)
            
            if pre_rendered_val is not None and os.path.exists("revenue_chart.png"):
                sum_30_days = pre_rendered_val
                path = "revenue_chart.png"
            else:
                path, sum_30_days = await generate_revenue_chart(session)
            photo = types.FSInputFile(path)
            
            services_text = "\n".join(
                f"  ▫️ {srv}: <code>{amount:.2f}</code> руб."
                for srv, amount in revenue_by_service.items()
            )
            if not services_text:
                services_text = "  ▫️ Нет успешных платежей"

            # Get latest 5 payments
            latest_payments = await db.payments_api.get_latest_payments(session, limit=5)
            attempts_lines = []
            for p in latest_payments:
                status_emoji = "🟢" if p.status == "successful" else "🔴"
                status_txt = "успешно" if p.status == "successful" else p.status
                attempts_lines.append(
                    f"  {status_emoji} <code>{p.amount}</code> руб. | {p.service} | {p.date} ({status_txt})"
                )
            attempts_text = "\n".join(attempts_lines) if attempts_lines else "  Нет платежей"
                
            caption = (
                f"<b>💰 Статистика доходов</b>\n\n"
                f"💵 Общий доход: <code>{total_revenue:.2f}</code> руб.\n"
                f"📈 Доход за последние 30 дней: <code>{sum_30_days:.2f}</code> руб.\n"
                f"🔄 Конверсия оплат: <code>{conv_rate:.2f}%</code>\n\n"
                f"💳 Доходы по сервисам:\n{services_text}\n\n"
                f"📝 <b>Последние 5 попыток оплаты:</b>\n{attempts_text}"
            )

        elif view == "activity":
            active_bots = await db.message_api.get_active_bots_count(session, days=30)
            total_suggestions = await db.message_api.get_total_suggestions_count(session)
            total_bots = (await session.execute(select(func.count(Bot.id)))).scalar() or 0
            
            if pre_rendered_val is not None and os.path.exists("activity_chart.png"):
                count_30_days = pre_rendered_val
                path = "activity_chart.png"
            else:
                path, count_30_days = await generate_activity_chart(session)
            photo = types.FSInputFile(path)

            # Get total and active senders count
            total_senders = (await session.execute(select(func.count(Sender.id)))).scalar() or 0
            active_senders = (await session.execute(select(func.count(Sender.id)).where(Sender.is_active == True))).scalar() or 0

            # Get Top-5 active bots in last 30 days
            min_timestamp = time.time() - (30 * 86400)
            stmt = (
                select(Bot.name, Bot.url, func.count(SuggestedMessage.primary_key).label("msg_count"))
                .join(SuggestedMessage, Bot.id == SuggestedMessage.bot_id)
                .where(cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger) >= min_timestamp)
                .group_by(Bot.id, Bot.name, Bot.url)
                .order_by(desc("msg_count"))
                .limit(5)
            )
            res = await session.execute(stmt)
            top_bots_data = res.all()
            top_bots_lines = []
            for index, (bot_name, bot_url, count_val) in enumerate(top_bots_data, 1):
                username = f"@{bot_url.split('/')[-1]}" if (bot_url and '/' in bot_url) else bot_name
                top_bots_lines.append(f"  {index}. <b>{username}</b>: <code>{count_val}</code> сообщений")
            top_bots_text = "\n".join(top_bots_lines) if top_bots_lines else "  Нет активности"

            caption = (
                f"<b>📊 Активность платформы</b>\n\n"
                f"🤖 Активных ботов (30 дней): <code>{active_bots}</code>\n"
                f"📈 Предложенных сообщений за последние 30 дней: <code>{count_30_days}</code>\n"
                f"📩 Всего предложенных сообщений: <code>{total_suggestions}</code>\n"
                f"🤖 Всего ботов в системе: <code>{total_bots}</code>\n"
                f"👥 Всего пользователей: <code>{total_senders}</code> (из них активных: <code>{active_senders}</code>)\n\n"
                f"🏆 <b>Топ-5 активных ботов (30 дней):</b>\n{top_bots_text}"
            )
        else:
            return

    if data == "show_incomes":
        await call.message.delete()
        sent_msg = await call.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=get_stats_markup()
        )
    else:
        sent_msg = await call.message.edit_media(
            media=types.InputMediaPhoto(media=photo, caption=caption),
            reply_markup=get_stats_markup()
        )

    # Cache the result (ttl=None because background task clears it)
    if not cached_data and sent_msg and sent_msg.photo:
        chart_cache.set(cache_key, (sent_msg.photo[-1].file_id, caption), ttl=None)
