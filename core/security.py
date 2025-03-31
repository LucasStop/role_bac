from datetime import datetime, timedelta
from core.user_data import load_user_data, save_user_data
from constants import LOCK_DURATION_MINUTES, MAX_LOGIN_ATTEMPTS

def check_account_locked(username):
    user_data = load_user_data()
    if username not in user_data:
        return False
    security = user_data[username].get("security", {})
    if not security.get("is_locked", False):
        return False
    lock_time_str = security.get("lock_time")
    if lock_time_str:
        lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
        unlock_time = lock_time + timedelta(minutes=LOCK_DURATION_MINUTES)
        if datetime.now() > unlock_time:
            user_data[username]["security"]["is_locked"] = False
            user_data[username]["security"]["failed_attempts"] = 0
            save_user_data(user_data)
            return False
    return True

def reset_failed_attempts(username):
    user_data = load_user_data()
    if username in user_data and "security" in user_data[username]:
        user_data[username]["security"]["failed_attempts"] = 0
        save_user_data(user_data)

def increment_failed_attempts(username):
    user_data = load_user_data()
    if username not in user_data:
        return 0
    if "security" not in user_data[username]:
        user_data[username]["security"] = {"failed_attempts": 0, "is_locked": False, "lock_time": None}
    user_data[username]["security"]["failed_attempts"] += 1
    attempts = user_data[username]["security"]["failed_attempts"]
    if attempts >= MAX_LOGIN_ATTEMPTS:
        user_data[username]["security"]["is_locked"] = True
        user_data[username]["security"]["lock_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_data)
    return attempts
