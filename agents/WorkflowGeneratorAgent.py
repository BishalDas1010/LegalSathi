import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()

load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    print("key is not found ")

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=API_KEY
)


planner_prompt = ChatPromptTemplate.from_template("""
You are the Workflow Planner.

Your job is NOT to answer the user's question.

Your job is ONLY to create the execution workflow.

Available Agents

- DocumentAnalysis
- OCR
- ClauseAnalysis
- LegalSearch
- CaseLawSearch
- CitationFinder
- DraftNotice
- DraftAgreement
- RiskAssessment
- Summarizer
- FinalAnswer

Rules

1. Think step by step.
2. Return ONLY JSON.
3. Never explain.
4. Choose only necessary agents.

User Query:

{query}

Document Present:

{document}

Output Format

{{
    "workflow":[
        "Agent1",
        "Agent2",
        "Agent3"
    ]
}}
""")




chain = planner_prompt | llm

class WorkflowPlannerAgent:
    def __init__(self, query: str, llm=None, document: bool = False):
        self.query = query
        self.llm = llm
        self.document = document

    def generate_workflow(self) -> list[str]:
        return plan_workflow(self.query, self.document)


def plan_workflow(query: str, document: bool) -> list:
    """
    Invoke the planner and return the list of agent names in the workflow.
    """
 
    doc_str = "True" if document else "False"
    
    response = chain.invoke({
        "query": query,
        "document": doc_str
    })
    
   
    content = response.content.strip()
 
    try:
        data = json.loads(content)
        workflow = data.get("workflow", [])
        return workflow
    except json.JSONDecodeError:

        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("workflow", [])
        else:
            raise ValueError("Could not parse JSON from planner response.")

# Example usage
if __name__ == "__main__":

    query1 = "Analyze this NDA and identify risky clauses."
    document1 = True
    workflow1 = plan_workflow(query1, document1)
    print("Workflow for NDA analysis:", workflow1)

 
    query2 = "Can my landlord evict me without notice?"
    document2 = False
    workflow2 = plan_workflow(query2, document2)
    print("Workflow for eviction question:", workflow2)

    query3 = "Analyze this employment agreement."
    document3 = True
    workflow3 = plan_workflow(query3, document3)
    print("Workflow for employment agreement:", workflow3)