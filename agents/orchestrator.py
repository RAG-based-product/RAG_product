from typing import Dict, List, Any
from agents.base_agent import BaseAgent

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflow_registry = {}
    
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent
    
    def register_workflow(self, workflow_name: str, agent_sequence: List[str]):
        self.workflow_registry[workflow_name] = agent_sequence
    
    async def process_message(self, user_message: str, user_id: str, workflow: str = "default") -> Dict[str, Any]:
        context = {
            "user_id": user_id,
            "conversation_history": await self._get_conversation_history(user_id),
            "current_workflow": workflow
        }
        
        agent_sequence = self.workflow_registry.get(workflow, ["research_agent", "analysis_agent"])
        
        results = {}
        for agent_name in agent_sequence:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = await agent.process(user_message, {**context, **results})
                results[agent_name] = result
        
        # final_response = await self._synthesize_final_response(results)
        
        # todo
        # await self._save_to_memory(user_id, user_message, final_response)
        
        # For now, just return the results dictionary as the final response
        final_response = results
        return final_response