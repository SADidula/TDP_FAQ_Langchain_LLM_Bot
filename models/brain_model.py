# import essential packages
import os

import random
from typing import NoReturn
from models.configurations import Configurator
from models.web_loader_model import Web_Loader

from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain.document_loaders.web_base import WebBaseLoader
from langchain_openai import OpenAI as openAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


class Brain:

    # init api
    def __init__(self, config: Configurator, crawler: Web_Loader) -> NoReturn:
        self.model_lang: str = 'gpt-3.5-turbo-instruct'
        self.model_open: str = 'gpt-3.5-turbo'
        
        # grabbing and setting api key
        api_key: str = config.get_configurations_value('llm configurations','api_key')
        os.environ['OPENAI_API_KEY'] = api_key

        # setting lanchain and web crawler environment for query search 
        loader = WebBaseLoader(crawler.get_sitemap())
        document = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=4000, separators=['\n', '\n\n', '', ' '])
        all_splits = text_splitter.split_documents(document)
        
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-large',
            dimensions=3072,
        )
                                
        self.document_search = FAISS.from_documents(all_splits, embeddings)
        
    def in_scope_search(self, question: str) -> str:
        response = ''
        retriever = self.document_search.as_retriever(search_type="similarity",search_kwargs={'k': 1})
        prompt = self.question_prompt_template()

        rag_chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | prompt
                    | openAI(temperature=0, model=self.model_lang)
                    | StrOutputParser()
                )
        
        for chunk in rag_chain.stream(question):
            response+=chunk
                                
        if not any(word in response for word in ['context','do not know',"don't know",'do not have']):
            return response
        else:
            return self.out_scope_search(question=question)
                           
    def out_scope_search(self, question: str) -> str:
        full_res = []
        result = ""
        for response in ChatOpenAI(temperature=0, model_name=self.model_open, streaming=True).stream(question):
            wordstream = response.dict().get('content')
            
            if wordstream:
                full_res.append(wordstream)
                result = "".join(full_res).strip()
        
        return result
    
    def predict_questions(self, question: str) -> list[str]:
        prompt = self.recommendation_prompt_template()

        rag_chain = (
                    {"question": RunnablePassthrough()}
                    | prompt
                    | openAI(temperature=1, model=self.model_lang)
                    | StrOutputParser()
                )
        
        result = rag_chain.invoke(question)
        recommended_ques = [rec.strip() for rec in result.split("\n") if rec.strip()]
        return recommended_ques
    
    def question_prompt_template(self) -> PromptTemplate:
        template = """Answer the question as precise as possible using the provided context.
        If you don't know the answer, say you don't know and at any given time do not make up any answers. 
        You are a Swinburne University of Technology assistant created for helping students, and any other users.
        
        CONTEXT: {context}
        
        QUESTION: {question}
        
        ANSWER:
        """
        
        return PromptTemplate(template=template, input_variables=["context", "question"])  
    
    def recommendation_prompt_template(self) -> PromptTemplate:
        template = """You are a helpful assistant in predicting maximum five questions based on the given question.
        When generating the question do not number or add symbols to the predictions at any given instance. If done so remove the numbers and symbols.
        
        QUESTION: {question}
        
        PREDICTION:
        """
        
        return PromptTemplate(template=template, input_variables=["question"])

        
