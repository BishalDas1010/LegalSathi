from typing import TypedDict
import json 
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os
from IntentClassifierAgent import IntentClassifier


load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    print("key is not found ")


class LegalState(TypedDict):
    query: str
    workflow :list[str]
    result : dict




llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=API_KEY
)


def llm_route(query: str):
    """
    Fallback to LLM when keyword routing fails.
    """
    intent = IntentClassifier(query, llm)
    return intent.intent_classifier()




class SimpleLegalRouter:
    def __init__(self):
        # Keep the dictionary simple
        self.routes = {
            "DocumentAnalysis": ["analyze", "review", "extract", "compare", "clause", "risk"],
            "LegalResearch": ["research", "case law", "precedent", "statute", "ruling", "law on"],
            "Drafting": ["draft", "write", "generate", "create", "template", "contract"],
            "Summarization": ["summarize", "summary", "brief", "key points", "tldr"],
            "Translation": ["translate", "spanish", "french", "hindi", "language"],
            "ClientIntake": ["intake", "consultation", "injured", "accident", "lawsuit"],
            "Compliance": ["compliance", "monitor", "deadline", "audit", "gdpr"]
        }

    def route_query(self, query):
        clean_query = query.lower()
        matched_agents = []

        # Loop through each agent and their keywords
        for agent, keywords in self.routes.items():
            # If ANY keyword is found inside the query, add the agent
            if any(kw in clean_query for kw in keywords):
                matched_agents.append(agent)

        # Fallback if the list is empty
        if not matched_agents:
            return llm_route(query)

        return matched_agents


# Testing the simpler code

router = SimpleLegalRouter()

query1 = "Can you draft a new contract for me?"
print("Query 1 routes to:", router.route_query(query1))
# ['Drafting']

query2 = "Please summarize this case law document."
print("Query 2 routes to:", router.route_query(query2))
# ['LegalResearch', 'Summarization']

query3 = "I want to know whether my employer can terminate me without notice."
print("Query 3 routes to:", router.route_query(query3))
# Falls back to LLM