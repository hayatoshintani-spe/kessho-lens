"""
AIエージェントモジュール
4つのAI投資家エージェントを提供する
"""

from .base_agent import BaseAgent
from .buffett_agent import BuffettAgent
from .soros_agent import SorosAgent
from .lynch_agent import LynchAgent
from .flat_agent import FlatAgent

# 全エージェントのインスタンスを生成
ALL_AGENTS = {
    "buffett": BuffettAgent(),
    "soros": SorosAgent(),
    "lynch": LynchAgent(),
    "flat": FlatAgent(),
}


def get_agent(agent_id: str) -> BaseAgent:
    """エージェントIDからエージェントを取得"""
    return ALL_AGENTS.get(agent_id)


def get_all_agents():
    """全エージェントのリストを返す"""
    return list(ALL_AGENTS.values())


__all__ = [
    "BaseAgent",
    "BuffettAgent",
    "SorosAgent",
    "LynchAgent",
    "FlatAgent",
    "ALL_AGENTS",
    "get_agent",
    "get_all_agents",
]
