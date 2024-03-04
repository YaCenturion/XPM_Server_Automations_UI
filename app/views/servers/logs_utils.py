from app.models import *


def get_action_logs():
    rows = TasksHistory.query.order_by(TasksHistory.id.desc()).limit(100).all()
    return rows
