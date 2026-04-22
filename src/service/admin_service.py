from src.db import connection as db
from src.db import queries as q


def get_stats(start_date: str, end_date: str) -> dict:
    start = f"{start_date} 00:00:00"
    end = f"{end_date} 23:59:59"
    with db.get_db() as conn:
        row = q.fetch_stats_by_period(conn, start, end)
        total_balance = q.fetch_total_balance(conn)
        txs = q.fetch_transactions_by_period(conn, start, end)
        return {
            "total_charged": row["total_charged"],
            "total_used": row["total_used"],
            "total_balance": total_balance,
            "transactions": [dict(t) for t in txs],
        }
