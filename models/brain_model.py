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
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


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
        self.document_search = FAISS.from_documents(all_splits, embeddings)
        
    def in_scope_search(self, question: str) -> str:
        retriever = self.document_search.as_retriever(search_type="similarity", search_kwargs={"k": 1})
        prompt = self.question_prompt_template()

        rag_chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | prompt
                    | openAI(temperature=0, model='gpt-3.5-turbo-instruct')
                    | StrOutputParser()
                )
        
        result = rag_chain.invoke(question)
        
        if not any(word in result for word in ['context','do not know',"don't know",'do not have']):
            return result
        else:
            return self.out_scope_search(question=question)
              
    def out_scope_search(self, question: str) -> str:
        response = OpenAI().chat.completions.create(
            model='gpt-3.5-turbo-instruct',
            messages=[
                {"role": "user", "content": question},
            ]
        )
        
        return response.choices[0].message.content
        
    def question_prompt_template(self) -> PromptTemplate:
        template = """Answer the question as precise as possible using the provided context.
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        You are a helpful university FAQ assistant.
        
        CONTEXT: {context}
        
        QUESTION: {question}
        
        ANSWER:
        """
        
        return PromptTemplate(template=template, input_variables=["context", "question"])  

        
