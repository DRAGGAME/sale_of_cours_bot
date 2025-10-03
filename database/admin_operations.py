from database.user_operation import UserOperation


class AdminOperation(UserOperation):

    async def insert_new_user(self, chat_id: str):
        await self.execute_query("""
        INSERT INTO user_data (chat_id) VALUES ($1);
        """, (chat_id,))

    async def insert_new_transaction(self, chat_id: str, name_transaction, transaction_id, amount):
        await self.execute_query("""INSERT INTO all_transaction (chat_id, name_transaction, transaction_id, amount)
                                    VALUES ($1, $2, $3, $4);""", (chat_id, name_transaction, transaction_id, amount))

