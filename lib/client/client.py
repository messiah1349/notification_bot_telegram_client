import logging
from telegram import ReplyKeyboardRemove, Update, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

import lib.utils.utils as ut
import lib.client.print_functions as pf
import lib.client.keyboards as kb
from lib.backend import AbstractBackendRequester

menu_names = ut.get_menu_names()

# Enable logging
logger = logging.getLogger(__name__)


class Client:

    @dataclass()
    class States:
        MAIN_MENU_CHOSE: int
        PROCESS_DEED_NAME: int
        PROCESS_NOTIFICATION_FACT: int
        PROCESS_NOTIFICATION_TIME: int
        PROCESS_RENAME_DEED_NAME: int
        PROCESS_TIME: int

    def __init__(self, token: str, backend_requester: AbstractBackendRequester):
        self.backend: AbstractBackendRequester = backend_requester
        self.application = Application.builder().token(token).build()
        self.states = self.get_states()
        logger.info('client was inited')

    def get_states(self):
        states = self.States(*range(6))
        return states

    @staticmethod
    def reset_notification_job(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            logger.info(f"Job {name=} does not exist at jobs")
            return False
        logger.info(f"Job name =  {name}. Start to remove all jobs")
        for job in current_jobs:
            job.schedule_removal()
            logger.info(f"Job {job=} removed")
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        markup = kb.get_start_keyboard()
        text = pf.chose_move()
        await update.message.reply_text(
            text,
            reply_markup=markup
        )
        return self.states.MAIN_MENU_CHOSE

    async def show_deeds(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        response = await self.backend.get_deed_for_user(user_id)
        deeds = response.answer
        markup = kb.get_inline_deeds(deeds)
        text = pf.this_is_deeds()
        await update.message.reply_text(
            text,
            reply_markup=markup
        )

        return self.states.MAIN_MENU_CHOSE

    async def add_deed(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        text = pf.deed_name_questions()
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove()
        )

        return self.states.PROCESS_DEED_NAME

    async def process_deed_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        deed_name = update.message.text
        user_id = update.message.from_user.id
        response = await self.backend.add_deed(user_id, deed_name)
        deed_js = response.answer
        deed = json.loads(deed_js)
        deed_id = deed['id']
        context.user_data['deed_id'] = deed_id

        markup = kb.bool_variants()
        text = f"{pf.deed_added()}\n\n{pf.notification_questions()}"
        await update.message.reply_text(
            text,
            reply_markup=markup
        )

        return self.states.PROCESS_NOTIFICATION_FACT

    async def process_notification_fact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = update.message.text

        if text == menu_names.no_:
            del context.user_data['deed_id']
            markup = kb.get_start_keyboard()
            await update.message.reply_text(
                "Oк!",
                reply_markup=markup
            )
            return self.states.MAIN_MENU_CHOSE

        elif text == menu_names.yes_:

            markup = kb.get_days()
            text = f"{pf.chose_day()}:"

            await update.message.reply_text(
                text,
                reply_markup=markup
            )
            return self.states.MAIN_MENU_CHOSE

    async def process_day_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        day_timedelta = int(query.data.split('=')[1])
        date = ut.localize(datetime.now() + timedelta(days=day_timedelta))

        context.user_data['date'] = date
        markup = kb.get_hours()
        text = f"{ut.repr_date(date)}\n{pf.chose_hour()}:"

        await query.edit_message_text(text=text, reply_markup=markup)

        return self.states.MAIN_MENU_CHOSE

    async def process_hour_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        ex_text = query.message.text
        ex_text = ex_text.split('\n')[0]
        await query.answer()

        hour = int(query.data.split('=')[1])
        context.user_data['hour'] = hour
        markup = kb.get_minutes()
        text = f"{ex_text},{hour}\n{pf.chose_minute()}:"
        await query.edit_message_text(text=text, reply_markup=markup)

        return self.states.MAIN_MENU_CHOSE

    async def process_minute_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        minute = int(query.data.split('=')[1])
        date = context.user_data['date']
        hour = context.user_data['hour']

        notification_time = date.replace(hour=hour, minute=minute, second=0)

        if notification_time < ut.localize(datetime.now()):
            markup = kb.get_days()
            text = pf.time_passed()
            await query.edit_message_text(text=text, reply_markup=markup)
            return self.states.MAIN_MENU_CHOSE

        del context.user_data['date']
        del context.user_data['hour']

        deed_id = context.user_data['deed_id']
        del context.user_data['deed_id']

        await self.setup_notification(deed_id, notification_time, query)

        return self.states.MAIN_MENU_CHOSE

    async def setup_notification(
        self,
        deed_id: int,
        notification_time: datetime,
        query: CallbackQuery
    ) -> None:
        response = await self.backend.add_notification(deed_id, notification_time)

        if response.status == 200:
            markup = kb.dzyn_keyboard()
            text = pf.wow()
            await query.edit_message_text(text=text, reply_markup=markup)

            markup = kb.get_start_keyboard()
            text = f"{pf.notify_added()} {ut.repr_date(notification_time, time_=True)}"
            await query.message.reply_text(
                text,
                reply_markup=markup
            )
        else:
            markup = kb.get_start_keyboard()
            text = f"{pf.internal_error()}"
            await query.message.reply_text(
                text,
                reply_markup=markup
            )

        return self.states.MAIN_MENU_CHOSE

    async def process_postpone_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        minutes = int(query.data.split('=')[1])
        notification_time = ut.localize(
            datetime.now()) + timedelta(minutes=minutes)

        deed_id = context.user_data['deed_id']
        del context.user_data['deed_id']

        await self.setup_notification(deed_id, notification_time, query)

        return self.states.MAIN_MENU_CHOSE

    async def process_deed_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        deed_id = int(query.data.split('=')[1])
        response = await self.backend.get_deed(deed_id)
        deed = response.answer
        inline_markup = kb.get_inline_deed(deed)

        text = deed.name
        if deed.notify_time:
            text = text + \
                f'\n🔔- {ut.repr_date(ut.localize(deed.notify_time), time_=True)}'

        await query.message.reply_text(
            text,
            reply_markup=inline_markup
        )

    async def process_done_deed_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        deed_id = int(query.data.split('=')[1])
        response = await self.backend.mark_deed_as_done(deed_id)
        text = pf.deed_done()
        if response.status == 200:
            text += f". {pf.notification_canceled()}"

        markup = kb.get_start_keyboard()
        await query.message.reply_text(
            text,
            reply_markup=markup
        )

        return self.states.MAIN_MENU_CHOSE

    async def process_reschedule_deed_after_notify_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        deed_id = int(query.data.split('=')[1])

        context.user_data['deed_id'] = deed_id

        markup = kb.get_days()
        text = f"{pf.chose_day()}:"

        await query.message.reply_text(
            text,
            reply_markup=markup
        )
        return self.states.MAIN_MENU_CHOSE

    async def process_rename_deed_name_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        deed_id = int(query.data.split('=')[1])
        context.user_data['deed_id'] = deed_id
        text = f"{pf.text_new_deed_name()}:"

        await query.message.reply_text(
            text
        )

        return self.states.PROCESS_RENAME_DEED_NAME

    async def process_rename_deed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        deed_id = context.user_data['deed_id']
        response = await self.backend.rename_deed(deed_id, text)

        markup = kb.get_start_keyboard()
        text = pf.deed_renamed()
        await update.message.reply_text(
            text,
            reply_markup=markup
        )

        return self.states.MAIN_MENU_CHOSE

    async def process_dzyn_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        text = pf.dzyn()

        await query.message.reply_text(
            text,
        )

        return self.states.MAIN_MENU_CHOSE

    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

    def build_conversation_handler(self):
        conv_handler = ConversationHandler(
            allow_reentry=True,
            entry_points=[
                CommandHandler("start", self.start),
                CallbackQueryHandler(
                    self.process_done_deed_callback, pattern="^notify_done_deed_id="),
                CallbackQueryHandler(self.process_reschedule_deed_after_notify_callback,
                                     pattern="^(notify_timer_deed_id=|timer_deed_id=)")
            ],
            states={
                self.states.MAIN_MENU_CHOSE: [
                    MessageHandler(filters.Regex(ut.name_to_reg(
                        menu_names.show_deeds)), self.show_deeds),
                    MessageHandler(filters.Regex(ut.name_to_reg(
                        menu_names.add_deed)), self.add_deed),
                    CallbackQueryHandler(
                        self.process_deed_callback, pattern="^deed_id="),
                    CallbackQueryHandler(
                        self.process_done_deed_callback, pattern="^done_deed_id="),
                    CallbackQueryHandler(
                        self.process_rename_deed_name_callback, pattern="^rename_deed_id="),
                    CallbackQueryHandler(
                        self.process_day_callback, pattern="^day="),
                    CallbackQueryHandler(
                        self.process_hour_callback, pattern="^hour="),
                    CallbackQueryHandler(
                        self.process_minute_callback, pattern="^minute="),
                    CallbackQueryHandler(
                        self.process_postpone_callback, pattern="^postpone="),
                    CallbackQueryHandler(
                        self.process_dzyn_callback, pattern=ut.name_to_reg('dzyn')),
                ],
                self.states.PROCESS_DEED_NAME: [
                    MessageHandler(filters.TEXT, self.process_deed_name)
                ],
                self.states.PROCESS_NOTIFICATION_FACT: [
                    MessageHandler(filters.Regex(
                        f"{menu_names.yes_}|{menu_names.no_}"), self.process_notification_fact),
                ],
                self.states.PROCESS_RENAME_DEED_NAME: [
                    MessageHandler(filters.TEXT, self.process_rename_deed)
                ],
            },
            fallbacks=[MessageHandler(filters.Regex("^Done$"), self.done)],
        )

        return conv_handler

    def build_application(self):
        logger.info('start to initialize app')
        conv_handler = self.build_conversation_handler()
        self.application.add_handler(conv_handler)
        self.application.run_polling(drop_pending_updates=True)
