from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    first_name = State()
    last_name = State()
    employee_number = State()


class SubmissionState(StatesGroup):
    waiting_for_content = State()


class AdminReplyState(StatesGroup):
    waiting_for_reply = State()
