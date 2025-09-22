from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


def build_rag_chain(retriever: Any):
    """Build a simple RAG chain: retriever → prompt → Gemini chat → string output.

    The prompt instructs the model to answer strictly from the provided context.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant that answers questions based on the provided context.
        Answer the user's question based only on the following context.
        If the answer is not available in the context, say 'I could not find an answer in the provided document.'

        Context:
        {context}

        Question:
        {question}
        """
    )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return chain


