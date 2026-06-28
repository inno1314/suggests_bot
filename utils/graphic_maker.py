import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import asyncio
import time
import logging

from database.model import AdMessageViews

logger = logging.getLogger(__name__)

# Constants for consistent, modern look
FONT_TITLE = {"fontsize": 13, "fontweight": "bold", "color": "#2c3e50", "pad": 15}
FONT_LABEL = {"fontsize": 10, "fontweight": "bold", "color": "#34495e", "labelpad": 10}
GRID_COLOR = "#e2e8f0"
SPINE_COLOR = "#cbd5e1"
BACKGROUND_COLOR = "#f8fafc"


class ChartCache:
    def __init__(self):
        self.cache = {}  # key -> (value, timestamp, ttl)

    def get(self, key: str):
        if key in self.cache:
            val, ts, ttl = self.cache[key]
            if ttl is not None and time.time() - ts > ttl:
                del self.cache[key]
                return None
            return val
        return None

    def set(self, key: str, val, ttl=300):
        self.cache[key] = (val, time.time(), ttl)

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]


chart_cache = ChartCache()


def apply_common_styles(ax, title, xlabel, ylabel):
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.set_title(title, **FONT_TITLE)
    ax.set_xlabel(xlabel, **FONT_LABEL)
    ax.set_ylabel(ylabel, **FONT_LABEL)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.tick_params(colors="#475569", labelsize=9)


# Synchronous helper functions for plotting in thread executor
def _render_view_count_chart(dates, counts):
    _, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")

    # Modern smooth line with customized marker
    ax.plot(
        dates,
        counts,
        marker="o",
        color="#3b82f6",
        linewidth=2.5,
        markersize=6,
        markerfacecolor="#ffffff",
        markeredgewidth=2,
        markeredgecolor="#3b82f6",
        label="Просмотры",
    )

    # Fill area under the curve for a premium look
    ax.fill_between(dates, counts, color="#3b82f6", alpha=0.1)

    apply_common_styles(
        ax, "Количество просмотров за последний месяц", "Дата", "Количество просмотров"
    )
    ax.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

    date_format = DateFormatter("%d.%m")
    ax.xaxis.set_major_formatter(date_format)

    plt.xticks(rotation=15)

    chart_path = "view_count_chart.png"
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close()
    return chart_path


def _render_revenue_chart(dates, succ_amounts, unsucc_amounts):
    x = np.arange(len(dates))
    width = 0.35

    _, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")

    # Grouped bars for successful and unsuccessful payments
    ax.bar(
        x - width / 2,
        succ_amounts,
        width,
        label="Успешные",
        color="#10b981",
        alpha=0.9,
        edgecolor="none",
    )
    ax.bar(
        x + width / 2,
        unsucc_amounts,
        width,
        label="Неуспешные",
        color="#ef4444",
        alpha=0.9,
        edgecolor="none",
    )

    apply_common_styles(ax, "Доходы за последние 30 дней", "Дата", "Сумма (руб.)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.6, color=GRID_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%d.%m") for d in dates], rotation=45, fontsize=9)
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0", loc="upper left")

    chart_path = "revenue_chart.png"
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close()
    return chart_path


def _render_activity_chart(dates, counts):
    _, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")

    # Modern smooth line and area fill
    ax.plot(
        dates,
        counts,
        marker="o",
        color="#f97316",
        linewidth=2.5,
        markersize=6,
        markerfacecolor="#ffffff",
        markeredgewidth=2,
        markeredgecolor="#f97316",
        label="Сообщения",
    )
    ax.fill_between(dates, counts, color="#f97316", alpha=0.1)

    apply_common_styles(
        ax,
        "Активность предложки за последние 30 дней",
        "Дата",
        "Количество предложенных сообщений",
    )
    ax.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

    date_format = DateFormatter("%d.%m")
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=15)

    chart_path = "activity_chart.png"
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close()
    return chart_path


def _render_bot_suggestions_chart(bot_id, dates, counts):
    _, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")

    ax.plot(
        dates,
        counts,
        marker="o",
        color="#6366f1",
        linewidth=2.5,
        markersize=6,
        markerfacecolor="#ffffff",
        markeredgewidth=2,
        markeredgecolor="#6366f1",
        label="Сообщения",
    )
    ax.fill_between(dates, counts, color="#6366f1", alpha=0.1)

    apply_common_styles(
        ax,
        "Статистика предложений за последние 30 дней",
        "Дата",
        "Количество предложенных сообщений",
    )
    ax.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

    date_format = DateFormatter("%d.%m")
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=15)

    chart_path = f"bot_suggestions_chart_{bot_id}.png"
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close()
    return chart_path


# Async wrappers using asyncio.to_thread
async def generate_view_count_chart(session: AsyncSession):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=29)

    stmt = (
        select(AdMessageViews)
        .where(AdMessageViews.view_date.between(start_date, end_date))
        .order_by(AdMessageViews.view_date)
    )

    result = await session.execute(stmt)
    views = result.scalars().all()
    count = sum(view.view_count for view in views)

    dates = [start_date + timedelta(days=x) for x in range(30)]
    view_counts = {view.view_date: view.view_count for view in views}
    counts = [view_counts.get(date, 0) for date in dates]

    chart_path = await asyncio.to_thread(_render_view_count_chart, dates, counts)
    return chart_path, count


async def generate_revenue_chart(session: AsyncSession) -> tuple[str, float]:
    from data.config import db

    trend = await db.payments_api.get_daily_revenue_trend(session, days=30)
    dates = list(trend.keys())

    succ_amounts = [val[0] for val in trend.values()]
    unsucc_amounts = [val[1] for val in trend.values()]
    total_revenue = sum(succ_amounts)

    chart_path = await asyncio.to_thread(
        _render_revenue_chart, dates, succ_amounts, unsucc_amounts
    )
    return chart_path, total_revenue


async def generate_activity_chart(session: AsyncSession) -> tuple[str, int]:
    from data.config import db

    trend = await db.message_api.get_platform_suggestions_trend(session, days=30)
    dates = list(trend.keys())
    counts = list(trend.values())
    total_suggestions = sum(counts)

    chart_path = await asyncio.to_thread(_render_activity_chart, dates, counts)
    return chart_path, total_suggestions


async def generate_bot_suggestions_chart(session: AsyncSession, bot_id: int) -> str:
    from data.config import db

    trend = await db.message_api.get_bot_suggestions_trend(
        session, bot_id=bot_id, days=30
    )
    dates = list(trend.keys())
    counts = list(trend.values())

    chart_path = await asyncio.to_thread(
        _render_bot_suggestions_chart, bot_id, dates, counts
    )
    return chart_path


async def pre_render_platform_charts(bot, db):
    logger.info("APS started pre-rendering platform charts...")
    async with db.session_maker() as session:
        # Pre-render views chart
        try:
            path, count = await generate_view_count_chart(session)
            chart_cache.set("pre_rendered_val:ads", count, ttl=None)
            chart_cache.delete("platform_stats:ads")
            logger.info(f"Pre-rendered views chart. Count: {count}")
        except Exception as e:
            logger.error(f"Failed to pre-render views chart: {e}")

        # Pre-render revenue chart
        try:
            path, sum_30_days = await generate_revenue_chart(session)
            chart_cache.set("pre_rendered_val:revenue", sum_30_days, ttl=None)
            chart_cache.delete("platform_stats:revenue")
            logger.info(f"Pre-rendered revenue chart. Sum: {sum_30_days}")
        except Exception as e:
            logger.error(f"Failed to pre-render revenue chart: {e}")

        # Pre-render activity chart
        try:
            path, count_30_days = await generate_activity_chart(session)
            chart_cache.set("pre_rendered_val:activity", count_30_days, ttl=None)
            chart_cache.delete("platform_stats:activity")
            logger.info(f"Pre-rendered activity chart. Count: {count_30_days}")
        except Exception as e:
            logger.error(f"Failed to pre-render activity chart: {e}")

    logger.info("APS completed pre-rendering platform charts")
