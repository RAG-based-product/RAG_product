from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate(self, messages: List[Dict], model: str, temperature: float) -> str:
        pass
