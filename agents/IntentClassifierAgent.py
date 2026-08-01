"""this file used to understand the user's query and help 
 supervisor to create the work flow"""

from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    print("key is not found ")


class IntentState(TypedDict):
    query : str
    intent : str



llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=API_KEY
)
#prompt 
prompt = ChatPromptTemplate.from_template("""
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

def intent_classifier(state: IntentState):

    chain = prompt | llm

    response = chain.invoke({
        "query": state["query"]
    })

    intent = response.content.strip()

    return {
        "query": state["query"],
        "intent": intent
    }
if __name__ == "__main__":

    state = {
        "query": "Find risky clauses in my employment agreement."
    }

    result = intent_classifier(state)

    print(result)