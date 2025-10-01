import asyncio

from database.user_operation import UserOperation

async def select_courses(sqlbase: UserOperation):
    courses = await sqlbase.select_all_courses()

    return courses

