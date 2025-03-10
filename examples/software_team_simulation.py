import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional

import typer

from metagpt.config2 import Config
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.context import Context
from metagpt.environment.env import MGXEnv
from metagpt.logs import logger
from metagpt.roles import Architect, Engineer2, ProductManager, DataAnalyst, TeamLeader
from metagpt.schema import AIMessage, UserMessage

app = typer.Typer(add_completion=False)


class SoftwareTeamSimulation:
    """Simulates a complete software development team with multiple roles"""

    def __init__(self,
                 context: Context,
                 project_idea: str,
                 output_dir: Optional[Path] = None,
                 debug: bool = False):
        self.context = context
        self.project_idea = project_idea
        self.output_dir = output_dir or DEFAULT_WORKSPACE_ROOT / uuid.uuid4(
        ).hex
        self.debug = debug
        self.env = None

        # 设置更详细的日志格式
        import logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        # 准备角色名称对应表，用于更易读的日志输出
        self.role_display_names = {
            "Mike": "TeamLeader",
            "Alice": "ProductManager",
            "Bob": "Architect",
            "Alex": "Engineer",
            "David": "DataAnalyst"
        }

    def _setup_environment(self) -> MGXEnv:
        """Set up the environment with all required roles"""
        logger.info(
            "Setting up environment with software development team roles")

        # Import role name constants
        from metagpt.const import TEAMLEADER_NAME

        # Create environment
        env = MGXEnv(context=self.context)

        # Create roles - each with their specific name in MetaGPT
        team_leader = TeamLeader()  # name="Mike"
        product_manager = ProductManager()  # name="Alice"
        architect = Architect()  # name="Bob"
        engineer = Engineer2()  # name="Alex"
        data_analyst = DataAnalyst()  # name="David"

        if self.debug:
            logger.info(
                f"Role names: TeamLeader={team_leader.name}, ProductManager={product_manager.name}, "
                f"Architect={architect.name}, Engineer={engineer.name}, DataAnalyst={data_analyst.name}"
            )

            # Example: Pre-populate architect with technical constraints
            architect.rc.memory.add(
                AIMessage(
                    content=
                    "The project should use Python with FastAPI for backend and React for frontend.",
                    sent_from="System"))

            # Example: Pre-populate product manager with market information
            product_manager.rc.memory.add(
                AIMessage(
                    content=
                    "Market research shows users need a simple and intuitive interface.",
                    sent_from="System"))

        # Add all roles to the environment
        env.add_roles(
            [team_leader, product_manager, architect, engineer, data_analyst])
        self.env = env
        return env

    def _log_message_flow(self, message):
        """Log message flow for debugging"""
        sender = message.sent_from or "User"
        sender_display = self.role_display_names.get(sender, sender)

        # 获取更易读的接收者名称
        receivers_raw = list(message.send_to) if message.send_to else ["All"]
        receivers = [self.role_display_names.get(r, r) for r in receivers_raw]
        receivers_str = ", ".join(receivers)

        # 创建消息预览
        content_preview = message.content[:150] + "..." if len(
            message.content) > 150 else message.content

        # 记录消息流向和内容
        logger.info(f"🔄 MESSAGE: {sender_display} ➡️ {receivers_str}")
        logger.info(f"📄 CONTENT: {content_preview}")
        logger.info(
            f"🏷️ METADATA: {message.metadata if message.metadata else 'None'}")

    async def run_simulation(self, max_rounds: int = 10):
        """Run the software development team simulation"""
        # Set up environment with all roles
        env = self._setup_environment()

        # 引入TeamLeader常量名称
        from metagpt.const import TEAMLEADER_NAME

        logger.info("💼 SIMULATION START: Creating initial user message")

        # Create and publish initial message from user with project idea
        initial_message = UserMessage(
            content=
            f"I want to build the following application: {self.project_idea}",
            send_to={TEAMLEADER_NAME
                     }  # Direct the initial message to TeamLeader (Mike)
        )

        self._log_message_flow(initial_message)

        logger.info("📣 PUBLISHING: Initial user message to environment")

        # Publish the initial message to the environment
        env.publish_message(
            initial_message,
            user_defined_recipient=TEAMLEADER_NAME,
        )

        # Run the environment until idle or max rounds reached
        round_count = 0
        while not env.is_idle and round_count < max_rounds:
            round_count += 1
            logger.info(
                f"🔄 ROUND {round_count}/{max_rounds} START ============================"
            )

            # 记录当前活跃角色
            active_roles = [
                self.role_display_names.get(r.name, r.name)
                for r in env.roles.values() if not r.is_idle
            ]
            logger.info(f"👥 ACTIVE ROLES: {', '.join(active_roles)}")

            # 记录每个角色的消息队列大小
            for role_name, role in env.roles.items():
                role_display = self.role_display_names.get(
                    role_name, role_name)
                msg_count = role.rc.msg_buffer.size if hasattr(
                    role.rc, 'msg_buffer') else 0
                logger.info(
                    f"📨 MESSAGES QUEUE: {role_display} has {msg_count} messages waiting"
                )

            # Run one round of the environment
            logger.info("⚙️ EXECUTING: Environment run cycle")
            await env.run()

            # 获取新增的消息
            if round_count > 1:
                prev_msg_count = getattr(self, '_prev_history_count', 0)
                curr_msg_count = env.history.count()
                new_msgs = curr_msg_count - prev_msg_count
                logger.info(
                    f"📊 NEW MESSAGES: {new_msgs} messages generated in this round"
                )

            # 保存当前消息数量以便下一轮比较
            self._prev_history_count = env.history.count()

            # 记录当前环境状态
            is_idle = env.is_idle
            logger.info(
                f"🔄 ROUND {round_count}/{max_rounds} END ============================"
            )
            logger.info(
                f"🛑 ENVIRONMENT STATUS: {'Idle' if is_idle else 'Active'}")

        logger.info(
            f"✅ SIMULATION COMPLETED: After {round_count} rounds with {len(env.history.messages)} total messages"
        )
        return env.history

    def print_conversation_summary(self, history):
        """Print a summary of the conversation flow"""
        logger.info("=== Conversation Flow Summary ===")
        logger.info(f"Total messages: {len(history.messages)}")

        # 准备角色名称对应表，用于更易读的日志输出
        role_display_names = {
            "Mike": "TeamLeader",
            "Alice": "ProductManager",
            "Bob": "Architect",
            "Alex": "Engineer",
            "David": "DataAnalyst"
        }

        for i, msg in enumerate(history.messages):
            # 获取更易读的发送者名称
            sender = msg.sent_from or "User"
            sender_display = role_display_names.get(sender, sender)

            # 获取更易读的接收者名称
            receivers_raw = list(msg.send_to) if msg.send_to else ["All"]
            receivers = [role_display_names.get(r, r) for r in receivers_raw]
            receivers_str = ", ".join(receivers)

            # 裁剪消息内容以便显示
            content_preview = msg.content[:100] + "..." if len(
                msg.content) > 100 else msg.content

            logger.info(
                f"{i+1}. {sender_display} -> {receivers_str}: {content_preview}"
            )


def run_demo():
    """Run the software team simulation with fixed parameters"""
    # 固定参数
    project_idea = "创建一个任务管理应用，包含用户登录、任务创建、分配和跟踪功能"
    max_rounds = 15
    debug = True

    # 初始化配置和上下文
    config = Config.default()
    ctx = Context(config=config)

    # 创建输出目录
    output_path = DEFAULT_WORKSPACE_ROOT / f"demo_{uuid.uuid4().hex[:8]}"
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Starting software team simulation for project: {project_idea}")
    logger.info(f"Output directory: {output_path}")
    logger.info(
        "Using roles: TeamLeader(Mike), ProductManager(Alice), Architect(Bob), Engineer(Alex), DataAnalyst(David)"
    )

    # 创建并运行模拟
    simulation = SoftwareTeamSimulation(context=ctx,
                                        project_idea=project_idea,
                                        output_dir=output_path,
                                        debug=debug)

    try:
        # 异步运行模拟
        history = asyncio.run(simulation.run_simulation(max_rounds=max_rounds))

        # 打印会话流程摘要
        simulation.print_conversation_summary(history)

        logger.info(
            f"Simulation completed successfully. Results available in: {output_path}"
        )
    except Exception as e:
        logger.error(f"Simulation failed with error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    return output_path


if __name__ == "__main__":
    run_demo()
