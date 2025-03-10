#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import asyncio
from typing import Any, Dict, Iterable, Optional, Set

from gymnasium import spaces
from gymnasium.core import ActType, ObsType
from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny

from ohm.base import BaseEnvironment, BaseRole
from ohm.base.base_env_space import BaseEnvAction, BaseEnvObsParams
from ohm.context import Context
from ohm.logs import logger
from ohm.memory import Memory
from ohm.schema import Message, SerializationMixin
from ohm.utils.common import is_send_to
from ohm.utils.git_repository import GitRepository

from ohm.constants import AGENT, IMAGES, MESSAGE_ROUTE_TO_ALL, TEAMLEADER_NAME
from ohm.logs import get_human_input
from ohm.utils.common import extract_and_encode_images
from ohm.roles.role import Role


class Environment(BaseEnvironment, BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)
    action_space: spaces.Space[ActType] = Field(default_factory=spaces.Space,
                                                exclude=True)
    observation_space: spaces.Space[ObsType] = Field(
        default_factory=spaces.Space, exclude=True)
    desc: str = Field(default="")  # 环境描述
    roles: dict[str, SerializeAsAny[BaseRole]] = Field(default_factory=dict,
                                                       validate_default=True)
    member_addrs: Dict[BaseRole, Set] = Field(default_factory=dict,
                                              exclude=True)
    history: Memory = Field(default_factory=Memory)  # For debug
    context: Context = Field(default_factory=Context, exclude=True)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        pass

    def observe(self, obs_params: Optional[BaseEnvObsParams] = None) -> Any:
        pass

    def step(
        self, action: BaseEnvAction
    ) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        pass

    def add_roles(self, roles: Iterable[BaseRole]):
        for role in roles:
            role.context = self.context
            role.set_env(self)
            self.roles[role.name] = role

    def publish_message(self, message: Message, peekable: bool = True) -> None:
        logger.info(f"publish_message: {message.dump()}")
        found = False
        for role, addrs in self.member_addrs.items():
            if is_send_to(message, addrs):
                role.put_message(message)
                found = True
        if not found:
            logger.warning(f"Message no recipients: {message.dump()}")
        self.history.add(message)

    async def run(self):
        futures = []
        logger.info(f'{",".join([role.name for role in self.roles.values()])}')
        for role in self.roles.values():
            if role.is_idle:
                continue
            future = role.run()
            futures.append(future)

        if futures:
            await asyncio.gather(*futures)

    def get_role(self, name: str) -> BaseRole:
        return self.roles.get(name, None)

    def role_names(self) -> list[str]:
        return [i.name for i in self.roles.values()]

    @property
    def is_idle(self):
        for r in self.roles.values():
            if not r.is_idle:
                return False
        return True

    def archive(self, auto_archive=True):
        if auto_archive and self.context.kwargs.get("project_path"):
            git_repo = GitRepository(self.context.kwargs.project_path)
            git_repo.archive()


class MGXEnv(Environment, SerializationMixin):

    direct_chat_roles: set[str] = set()

    is_public_chat: bool = True

    def _publish_message(self,
                         message: Message,
                         peekable: bool = True) -> bool:
        if self.is_public_chat:
            message.send_to.add(MESSAGE_ROUTE_TO_ALL)
        message = self.move_message_info_to_content(message)
        return super().publish_message(message, peekable)

    def publish_message(self,
                        message: Message,
                        user_defined_recipient: str = "",
                        publicer: str = "") -> bool:
        message = self.attach_images(message)
        tl = self.get_role(TEAMLEADER_NAME)

        if user_defined_recipient:
            # human user's direct chat message to a certain role
            for role_name in message.send_to:
                if self.get_role(role_name).is_idle:
                    self.direct_chat_roles.add(role_name)

            self._publish_message(message)

        elif message.sent_from in self.direct_chat_roles:
            self.direct_chat_roles.remove(message.sent_from)
            if self.is_public_chat:
                self._publish_message(message)

        elif publicer == tl.profile:
            if message.send_to == {"no one"}:
                return True
            self._publish_message(message)

        else:
            message.send_to.add(tl.name)
            self._publish_message(message)

        self.history.add(message)

        return True

    def get_addresses(self, obj):
        """Get the addresses of the object."""
        return self.member_addrs.get(obj, {})

    def set_addresses(self, obj, addresses):
        """Set the addresses of the object"""
        self.member_addrs[obj] = addresses

    async def ask_human(self, question: str, sent_from: Role = None) -> str:
        rsp = await get_human_input(question)
        return "Human response: " + rsp

    async def reply_to_human(self,
                             content: str,
                             sent_from: Role = None) -> str:
        return "SUCCESS, human has received your reply. Refrain from resending duplicate messages.  If you no longer need to take action, use the command ‘end’ to stop."

    def move_message_info_to_content(self, message: Message) -> Message:
        """Two things here:
        1. Convert role, since role field must be reserved for LLM API, and is limited to, for example, one of ["user", "assistant", "system"]
        2. Add sender and recipient info to content, making TL aware, since LLM API only takes content as input
        """
        converted_msg = message.model_copy(deep=True)
        if converted_msg.role not in ["system", "user", "assistant"]:
            converted_msg.role = "assistant"
        sent_from = converted_msg.metadata[
            AGENT] if AGENT in converted_msg.metadata else converted_msg.sent_from
        # When displaying send_to, change it to those who need to react and exclude those who only need to be aware, e.g.:
        # send_to={<all>} -> Mike; send_to={Alice} -> Alice; send_to={Alice, <all>} -> Alice.
        if converted_msg.send_to == {MESSAGE_ROUTE_TO_ALL}:
            send_to = TEAMLEADER_NAME
        else:
            send_to = ", ".join({
                role
                for role in converted_msg.send_to
                if role != MESSAGE_ROUTE_TO_ALL
            })
        converted_msg.content = f"[Message] from {sent_from or 'User'} to {send_to}: {converted_msg.content}"
        return converted_msg

    def attach_images(self, message: Message) -> Message:
        if message.role == "user":
            images = extract_and_encode_images(message.content)
            if images:
                message.add_metadata(IMAGES, images)
        return message
