from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from config import bot, PROVIDER_TOKEN
from database.admin_operations import AdminOperation
from keyboards.menu_fabric import FabricInline
from keyboards.menu_fabric import PayCourse
from logger import logger


class PayHandlers:
    """
    Класс для работ с оплатой
    """
    def __init__(self):
        self.bot = bot
        self.router_pay = Router()
        self.pay_fabric_kb = FabricInline()

        self.admin_database = AdminOperation()

        self.register_handlers_for_pay()

    def register_handlers_for_pay(self):
        self.router_pay.callback_query.register(self.pay_course, PayCourse.filter(F.action=="pay"))
        self.router_pay.pre_checkout_query.register(self.pre_checkout_handler)
        self.router_pay.message.register(self.successfall_paymant, F.successful_payment)
        self.router_pay.callback_query.register(self.cancel_paymant, PayCourse.filter(F.action=="cancel_payment"))

    async def pay_course(self, callback: CallbackQuery, state: FSMContext):
        data_course = await state.get_value('data_course')
        keyboard_payment = await self.pay_fabric_kb.payment_create_kb(data_course[-4])

        prices = [LabeledPrice(label='Оплата товара', amount=(data_course[2]*100))]
        msg = await callback.message.answer_invoice(
            title=data_course[1],
            description=f"Оплата курса {data_course[1] if len(data_course[1]) else ""}",
            payload=f"{data_course[1]}",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            send_email_to_provider=True,
            prices=prices,
            reply_markup=keyboard_payment
        )
        await state.update_data(msg_price=msg.message_id, id_channel=data_course[-3])

        await callback.answer()

    async def pre_checkout_handler(self, pre_checkout_query: PreCheckoutQuery, state: FSMContext):
        await pre_checkout_query.answer(ok=True)

    async def successfall_paymant(self, message: Message, state: FSMContext):
        msg_price: str = await state.get_value('msg_price')
        channel_id = await state.get_value('id_channel')
        link = None

        await bot.delete_message(message_id=int(msg_price), chat_id=message.chat.id)

        await self.admin_database.insert_new_transaction(str(message.chat.id),
                                                         message.successful_payment.invoice_payload.title(),
                                                         message.successful_payment.telegram_payment_charge_id,
                                                         message.successful_payment.total_amount)

        try:
            link = await bot.create_chat_invite_link(channel_id, member_limit=1)

            url_link = getattr(link, 'invite_link')
            await message.reply(f"Платеж на сумму {message.successful_payment.total_amount // 100} "
                                f"{message.successful_payment.currency} прошел успешно\n\nВот ваша ссылка на курс: {url_link}")
        except TelegramBadRequest:
            await message.reply("Произошла ошибка платежа")
            logger.error(f"Видимо, айди канала {channel_id} - не существует")


    async def cancel_paymant(self, callback: CallbackQuery):
        await callback.message.delete()

