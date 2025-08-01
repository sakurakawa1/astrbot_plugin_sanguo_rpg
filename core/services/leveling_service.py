# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : leveling_service.py
# @Software: AstrBot
# @Description: Service for handling character leveling

from ..domain.models import User, UserGeneral, UserGeneralDetails
from ..repositories.sqlite_user_repo import SqliteUserRepository
from ..repositories.sqlite_user_general_repo import SqliteUserGeneralRepository

class LevelingService:
    def __init__(self, user_repo: SqliteUserRepository, user_general_repo: SqliteUserGeneralRepository):
        self.user_repo = user_repo
        self.user_general_repo = user_general_repo

    def level_up_general(self, user_id: str, general_instance_id: int) -> str:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return "找不到玩家信息。"

        general_details = self.user_general_repo.get_by_instance_id(general_instance_id)
        if not general_details or general_details.user_id != user_id:
            return "找不到指定的武将。"

        # Create a UserGeneral instance to access business logic
        user_general = UserGeneral(
            instance_id=general_details.instance_id,
            user_id=general_details.user_id,
            general_id=general_details.general_id,
            level=general_details.level,
            exp=general_details.exp,
            created_at=general_details.created_at
        )

        exp_needed = user_general.get_exp_to_next_level()
        if user.exp < exp_needed:
            return f"经验不足，升级需要 {exp_needed} 经验，当前经验池有 {user.exp}。"

        # Deduct experience and level up
        user.exp -= exp_needed
        general_details.level += 1
        general_details.exp = 0  # Reset exp for the new level

        # Update database
        self.user_repo.update(user)
        self.user_general_repo.update(general_details)

        return f"恭喜！您的武将 {general_details.name} 已升至 {general_details.level} 级！"
