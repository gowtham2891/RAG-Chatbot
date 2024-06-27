import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")



prompt = ChatPromptTemplate.from_template(

    """
    Answer the folowing questions based only on the provided context.
    Think step by step before providing a detailed answer.
    I will tip you $1000 if user finds the answer helpful.
    <context>
    {context}
    </context>
    Question: {input}
    """

)




def load_docs(docs):

    loader = PyPDFLoader(docs)
    text_documents = loader.load() 

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_docs = text_splitter.split_documents(text_documents)
    vectors = FAISS.from_documents(final_docs, OpenAIEmbeddings())
    return vectors


    
def input(vectors):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain



def main():

    st.set_page_config("RAG")
    st.header("RAG Application")
    docs = load_docs("acsbr-016.pdf")
    retrieval_chain = input(docs)

    user_question = st.text_input("Ask question from the uploaded PDFs")
    if user_question:
        response = retrieval_chain.invoke({"input": user_question})
        result = response["answer"]
        st.write(result)


if __name__ == "__main__":
    main()
