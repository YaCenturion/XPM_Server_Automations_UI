from app.models import *


def get_action_logs(limiter=100):
    rows = TasksHistory.query.order_by(TasksHistory.id.desc()).limit(limiter).all()
    return rows
