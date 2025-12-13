from langchain_mistralai.chat_models import ChatMistralAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

class MistralLLMClient: 

    def __init__(self):

        load_dotenv() 

        self.API_KEY = os.getenv("MISTRAL_API_KEY") 
        
        # Si vous devez supporter le nom 'mistral' comme dans la deuxième version:
        if not self.API_KEY:
            self.API_KEY = os.getenv("mistral")

        # 3. Vérification
        if not self.API_KEY:
            raise ValueError("MISTRAL_API_KEY (ou 'mistral') non trouvée dans les variables d'environnement!")
        else:
            print("MISTRAL_API_KEY chargée avec succès!")
    
    async def generate(self, messages: List[Dict[str, Any]], model: str = "mistral-small-latest", temperature: float = 0.7) -> str:
        """
        Génère une réponse asynchrone en utilisant le modèle Mistral.
        """
        try:
            llm = ChatMistralAI(
                mistral_api_key=self.API_KEY,
                model_name=model,
                temperature=temperature,
            )

            result = await llm.ainvoke(messages)
            return result.content
        except Exception as e:
            
            raise Exception(f"Erreur API LLM Mistral: {str(e)}")
