"""
AIエージェントモジュール
7つのAI投資家エージェントを提供する（4ファンドメンバー + 3専門分析AI）
"""

from .base_agent import BaseAgent
from .buffett_agent import BuffettAgent
from .soros_agent import SorosAgent
from .lynch_agent import LynchAgent
from .flat_agent import FlatAgent
from .macro_agent import MacroAgent
from .quant_agent import QuantAgent
from .risk_agent import RiskAgent

# 全エージェント（会議参加者）
ALL_AGENTS = {
    "buffett": BuffettAgent(),
    "soros": SorosAgent(),
    "lynch": LynchAgent(),
    "flat": FlatAgent(),
    "macro": MacroAgent(),
    "quant": QuantAgent(),
    "risk": RiskAgent(),
}

# ポートフォリオ・取引に参加するファンドメンバー（元の4エージェント）
FUND_AGENTS = {
    "buffett": ALL_AGENTS["buffett"],
    "soros": ALL_AGENTS["soros"],
    "lynch": ALL_AGENTS["lynch"],
    "flat": ALL_AGENTS["flat"],
}


def get_agent(agent_id: str) -> BaseAgent:
    """エージェントIDからエージェントを取得"""
    return ALL_AGENTS.get(agent_id)


def get_all_agents():
    """全エージェントのリストを返す（7名全員）"""
    return list(ALL_AGENTS.values())


def get_fund_agents():
    """ファンド運用エージェント（ポートフォリオ・取引）のリストを返す"""
    return list(FUND_AGENTS.values())


__all__ = [
    "BaseAgent",
    "BuffettAgent",
    "SorosAgent",
    "LynchAgent",
    "FlatAgent",
    "MacroAgent",
    "QuantAgent",
    "RiskAgent",
    "ALL_AGENTS",
    "FUND_AGENTS",
    "get_agent",
    "get_all_agents",
    "get_fund_agents",
]
