from abc import ABC, abstractmethod
from typing import Dict, Any, List
from models.base_llm_client import BaseLLMClient

class BaseAgent(ABC):
    def __init__(self, name: str, llm_client: BaseLLMClient, system_prompt: str):
        self.name = name
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.tools = {}
        
    def register_tool(self, tool_name: str, tool_function: callable):
        self.tools[tool_name] = tool_function
    
    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод обработки сообщения"""
        pass
    
    async def _call_llm(self, prompt: str) -> str:
        """Вызов LLM с системным промптом"""
        return await self.llm_client.generate(prompt)