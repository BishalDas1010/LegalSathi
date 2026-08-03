"""this file used to understand the user's query and help 
 supervisor to create the work flow"""

from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate



class IntentState(TypedDict):
    query : str
    intent : str


class IntentClassifier:

    def __init__(self, query: str, llm):
        self.query = query
        self.llm = llm

        self.prompt = ChatPromptTemplate.from_template("""
You are an Intent Classifier for a Legal AI Assistant.

Your job is ONLY to classify the user's intent.

Possible intents are:

1. document_analysis
2. clause_extraction
3. risk_detection
4. missing_clause
5. legal_research
6. legal_drafting
7. compare_documents
8. translation
9. unknown

Return ONLY one intent.

User Query:
{query}
""")

    def intent_classifier(self):
        chain = self.prompt | self.llm

        response = chain.invoke({
            "query": self.query
        })

        return response.content.strip()