from abc import ABC, abstractmethod

class BaseHandler(ABC):
    def __init__(self, bot):
        self.bot = bot
    
    @abstractmethod
    def register_handlers(self, application):
        pass