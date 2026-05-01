# * Gonna import stuff as per needed.

class TimerManager:
    def __init__(self):
        self.user_timers = {} # user_id -> list of TimerTask

    def add_timer(self, user_id, timer):
        if user_id not in self.user_timers:
            self.user_timers[user_id] = []

        self.user_timers[user_id].append(timer)
    

    def remove_timer(self, user_id, timer):
        if user_id in self.user_timers:
            self.user_timers[user_id].remove(timer)

            if not self.user_timers[user_id]:
                del self.user_timers[user_id]

    
    def get_user_timers(self, user_id):
        return self.user_timers.get(user_id, [])
    

    def has_active_timer(self, user_id):
        return any(t.is_active() for t in self.get_user_timers(user_id))
    
    