# import essential packages
import os

import random
from typing import NoReturn
from models.configurations import Configurator
from models.web_loader_model import Web_Loader
from models.memory_model import Memory
from openai import OpenAI

# from tfIdfInheritVectorizer.feature_extraction.vectorizer import TFIDFVectorizer
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain.document_loaders.web_base import WebBaseLoader
from langchain_openai import OpenAI as openAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class Brain:

    # init api
    def __init__(self, config: Configurator, crawler: Web_Loader, memory: Memory) -> NoReturn:
        self.memory = memory
        self.model: str = 'gpt-3.5-turbo-instruct'
        
        # grabbing and setting api key
        api_key: str = config.get_configurations_value('llm configurations','api_key')
        os.environ['OPENAI_API_KEY'] = api_key

        # setting lanchain and web crawler environment for query search 
        loader = WebBaseLoader(crawler.get_sitemap())
        document = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, length_function=len, separators=['\n\n', '\n', ' ', '' ])
        all_splits = text_splitter.split_documents(document)
        
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-large',
            dimensions=3072,
        )
        self.document_search = FAISS.from_documents(all_splits, embeddings)
        
    def in_scope_search(self, question: str) -> str:
        retriever = self.document_search.as_retriever(search_type="similarity",search_kwargs={'k': 6, 'lambda_mult': 0.25, 'score_threshold': 0.85})
        prompt = self.question_prompt_template()

        rag_chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | prompt
                    | openAI(temperature=0, model=self.model)
                    | StrOutputParser()
                )
        
        result = rag_chain.invoke(question)
        
        return result
              
    def out_scope_search(self, question: str) -> str:
        response = OpenAI().chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": question},
            ]
        )
        
        return response.choices[0].message.content
    
    def question_prompt_template(self) -> PromptTemplate:
        template = """Answer the question as precise as possible using the provided context.
        If you don't know the answer, just say that you answer is not related to the FAQs and make up the answer for the question. 
        You are a helpful university assistant.
        
        CONTEXT: {context}
        
        QUESTION: {question}
        
        ANSWER:
        """
        
        return PromptTemplate(template=template, input_variables=["context", "question"])  

        
