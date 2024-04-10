# import essential packages
import os

from typing import NoReturn
from models.configurations import Configurator
from models.web_loader_model import Web_Loader
from models.memory_model import Memory
from openai import OpenAI

from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain.document_loaders.web_base import WebBaseLoader
from langchain_openai import OpenAI as openAI
from langchain.chains import ConversationalRetrievalChain


class Brain_Model:

    # init api
    def __init__(self, config: Configurator, crawler: Web_Loader, memory: Memory) -> NoReturn:
        self.memory = memory
        
        # grabbing and setting api key
        api_key: str = config.get_configurations_value('llm configurations','api_key')
        os.environ['OPENAI_API_KEY'] = api_key

        # setting lanchain and web crawler environment for query search 
        loader = WebBaseLoader(crawler.get_sitemap())
        document = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(separators="\n", chunk_size=800, chunk_overlap=200)
        all_splits = text_splitter.split_documents(document)
        
        embeddings = OpenAIEmbeddings()
        document_search = FAISS.from_documents(all_splits, embeddings)

        self.chain = ConversationalRetrievalChain.from_llm(openAI(temperature=0, model='gpt-3.5-turbo'), document_search.as_retriever(), return_source_documents=True)
        
    def in_scope_search(self, question: str) -> NoReturn:
       # attaching chat history
       result = self.chain({"question": question, "chat_history": self.memory.get_memory()})
       
       if not any(word in result['answer'] for word in ['context','do not know',"don't know",'do not have']):
            # self.memory.set_memory(ques=question,ans=result['answer'])
            print('\n'+result['answer'])
            return
       else:
            self.out_scope_search(question=question)
            return
       
       
    def out_scope_search(self, question: str) -> None:
        response = OpenAI().chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful FAQ assistant."},
                {"role": "user", "content": question},
            ]
        )
        
        print(response.choices[0].message.content)
        

        
