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
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, length_function=len, separators=['\n\n', '\n', ' ', '' ])
        all_splits = text_splitter.split_documents(document)
        
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-large',
            dimensions=3072,
        )
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
        
    # def get_recommendations(self, context: str) -> list:
    #     # Use your document search to retrieve relevant contexts
    #     retriever = self.document_search.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    #     similar_contexts = retriever(context)

    #     # Extract questions from similar contexts
    #     recommended_questions = []
    #     for similar_context in similar_contexts:
    #         recommended_questions.extend(self.memory.get_questions(similar_context))  # Assuming memory stores questions for contexts

    #     # Remove duplicates and limit the number of recommendations
    #     recommended_questions = list(set(recommended_questions))[:5]  # Adjust the number as needed

    #     # If there are not enough recommendations, randomly sample from the memory
    #     while len(recommended_questions) < 5:
    #         random_question = random.choice(self.memory.get_all_questions())
    #         recommended_questions.append(random_question)

    #     return recommended_questions
    
    # def get_recommendations(self, question: str, num_recommendations: int = 3) -> list[str]:
    #     # Calculate TF-IDF vectors for all FAQs
    #     vectorizer = TfidfVectorizer()
    #     faqs = self.memory.get_memory()
    #     tfidf_matrix = vectorizer.fit_transform([faq[0] for faq in faqs])

    #     # Calculate cosine similarity between user's question and all FAQs
    #     query_vector = vectorizer.transform([question])
    #     cosine_similarities = linear_kernel(query_vector, tfidf_matrix).flatten()

    #     # Get indices of top N most similar FAQs
    #     similar_indices = cosine_similarities.argsort()[:-num_recommendations-1:-1]

    #     # Get the actual FAQs for the top N indices
    #     recommendations = [faqs[i][0] for i in similar_indices]

    #     return recommendations
    
    def question_prompt_template(self) -> PromptTemplate:
        template = """Answer the question as precise as possible using the provided context.
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        You are a helpful university FAQ assistant.
        
        CONTEXT: {context}
        
        QUESTION: {question}
        
        ANSWER:
        """
        
        return PromptTemplate(template=template, input_variables=["context", "question"])  

        
