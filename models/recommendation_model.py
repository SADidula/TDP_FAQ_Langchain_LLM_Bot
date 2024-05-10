import os
from models.memory_model import Memory
from models.configurations import Configurator

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI

class Recommendation:
    def __init__(self, config: Configurator, memory: Memory):
        self.memory = memory
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)
        self.setup_recommendation_chain()

        # Grab and set API key
        api_key: str = config.get_configurations_value('llm configurations','api_key')
        os.environ['OPENAI_API_KEY'] = api_key

    def setup_recommendation_chain(self):
        template = """You are a helpful assistant in predicting next question based on chat history.
        Current conversation: {history}
        Human: {input}
        AI: Predicted Questions:"""
        PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
        self.recommendation_chain = LLMChain(llm=self.llm, prompt=PROMPT)

    def get_recommendations(self, question):
        chat_history = "\n".join([f"Human: {q}\nAI: {a}" for q, a in self.memory.get_memory()])
        print("Chat history:", chat_history)
        result = self.recommendation_chain.run(history=chat_history, input=question)
        print("Result from conversation_chain.predict:", result)
        recommendations = [rec.strip() for rec in result.split("\n") if rec.strip()]
        return recommendations
    

    

    