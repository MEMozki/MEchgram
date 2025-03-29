class FSMContext:
    def __init__(self):
        self._states = {}
    def set_state(self, user_id, state):
        self._states[user_id] = state
    def get_state(self, user_id):
        return self._states.get(user_id)
    def reset_state(self, user_id):
        if user_id in self._states:
            del self._states[user_id]