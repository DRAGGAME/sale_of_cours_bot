from database.user_operation import UserOperation


class AdminOperation(UserOperation):

    async def insert_new_user(self, chat_id: str):
        await self.execute_query("""
        INSERT INTO user_data (chat_id) VALUES ($1);
        """, (chat_id,))

