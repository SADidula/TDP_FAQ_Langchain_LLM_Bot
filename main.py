from typing import NoReturn, Tuple
from models.brain_model import  Brain_Model
from models.web_loader_model import  Web_Loader
from models.configurations import  Configurator
from models.memory_model import Memory

# instantiate class objects
config: Configurator = Configurator()
memory: Memory = Memory()
crawler: Web_Loader = Web_Loader(config=config)
brain: Brain_Model = Brain_Model(config=config, crawler=crawler, memory=memory)

def search(query: str) -> str:
    response = brain.in_scope_search(query)
    # recommendations = brain.get_recommendations(query)
    # return response, recommendations
    return response

# def get_recommendations(query: str) -> str:
#     return brain.get_recommendations(question=query)

# if __name__ == '__main__':
#     while True:
#         brain.in_scope_search(str(input("\nWhat to search? ")))