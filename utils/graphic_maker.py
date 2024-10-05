import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.model import AdMessageViews


async def generate_view_count_chart(session: AsyncSession):
    end_date = datetime.today().date() + timedelta(days=1)
    start_date = end_date - timedelta(days=30)

    stmt = (
        select(AdMessageViews)
        .where(AdMessageViews.view_date.between(start_date, end_date))
        .order_by(AdMessageViews.view_date)
    )

    result = await session.execute(stmt)
    views = result.scalars().all()
    count = 0
    for view in views:
        count += view.view_count

    dates = [start_date + timedelta(days=x) for x in range(31)]
    view_counts = {view.view_date: view.view_count for view in views}
    counts = [view_counts.get(date, 0) for date in dates]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker="o")
    plt.xlabel("Дата")
    plt.ylabel("Количество просмотров")
    plt.title("Количество просмотров за последний месяц")
    plt.grid(True)

    date_format = DateFormatter("%d.%m")
    plt.gca().xaxis.set_major_formatter(date_format)

    chart_path = "view_count_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path, count
