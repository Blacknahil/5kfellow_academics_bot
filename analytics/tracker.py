from file_manager.postgres_store import _get_async_connection


async def track_user(user_id: int):
    """Insert a user if new, otherwise update last_seen.
    """
    async with await _get_async_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users(user_id, first_seen, last_seen)
                VALUES (%s, NOW(), NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET last_seen = NOW();
                """,
                (user_id,),
            )


async def track_request():
    """ Increment request counter for the current day.
    """
    async with await _get_async_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO daily_stats (date, requests)
                VALUES (CURRENT_DATE, 1)
                ON CONFLICT (date)
                DO UPDATE SET requests = daily_stats.requests + 1
                """
            )

async def track_download(department: str):
    """ Increment download counter for the current day and department.
    """
    async with await _get_async_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO daily_stats (date, downloads)
                VALUES (CURRENT_DATE, 1)
                ON CONFLICT (date)
                DO UPDATE SET downloads = daily_stats.downloads + 1
                """
            )
            await cur.execute(
                """
                INSERT INTO department_stats (department, downloads)
                VALUES (%s, 1)
                ON CONFLICT (department)
                DO UPDATE SET downloads = department_stats.downloads + 1
                """,
                (department,),
            )


async def track_failed():
    async with await _get_async_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO daily_stats (date, failed)
                VALUES (CURRENT_DATE, 1)
                ON CONFLICT (date)
                DO UPDATE SET failed = daily_stats.failed + 1
                """
            )


async def get_stats():
    async with await _get_async_connection() as conn:
        async with conn.cursor() as cur:

            # total users ever
            await cur.execute("SELECT COUNT(*) FROM users")
            row = await cur.fetchone()
            total_users = row[0] if row is not None else 0

            # users active today
            await cur.execute("""
                SELECT COUNT(*)
                FROM users
                WHERE last_seen::date = CURRENT_DATE
            """)
            row = await cur.fetchone()
            users_today = row[0] if row is not None else 0

            # today's stats
            await cur.execute("""
                SELECT requests, downloads, failed
                FROM daily_stats
                WHERE date = CURRENT_DATE
            """)
            row = await cur.fetchone()
            if row is not None:
                requests_today, downloads_today, failed_today = row
            else:
                requests_today, downloads_today, failed_today = (0,0,0)

            # total requests
            await cur.execute("SELECT COALESCE(SUM(requests),0) FROM daily_stats")
            row = await cur.fetchone()
            total_requests = row[0] if row is not None else 0

            # total downloads
            await cur.execute("SELECT COALESCE(SUM(downloads),0) FROM daily_stats")
            row = await cur.fetchone()
            total_downloads = row[0] if row is not None else 0
            
            # most active department
            await cur.execute(
                """
                SELECT department
                FROM department_stats
                ORDER BY downloads DESC
                LIMIT 1
                """
            )

            row = await cur.fetchone()
            top_department = row[0] if row is not None else "N/A"

    return {
        "total_users": total_users,
        "users_today": users_today,
        "requests_today": requests_today,
        "total_requests": total_requests,
        "downloads_today": downloads_today,
        "total_downloads": total_downloads,
        "failed_today": failed_today,
        "top_department": top_department
    }