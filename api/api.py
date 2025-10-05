import dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
import os

from prompts import cypher_generation_prompt, cypher_qa_prompt, schema

# Connect to the .env file and read the contents
dotenv.load_dotenv()

# Instantiates GPT
llm = ChatOpenAI(
    model_name="gpt-5-nano",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# Connects to the Neo4j instance
graph = Neo4jGraph(
    url=os.getenv("NEO4J_CONNECTION_URL"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Prompt templates
cypher_prompt = PromptTemplate(
    template=cypher_generation_prompt,
    input_variables=["schema", "question"]
)
qa_prompt = PromptTemplate(
    template=cypher_qa_prompt,
    input_variables=["context", "question"]
)


# Instantiates FastAPI
app = FastAPI(title="Neo4j Conversational API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

chat_history = []
@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        # Create the LangChain Cypher + QA chain
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            input_key="question",
            allow_dangerous_requests=True
        )

        # Pass natural language question and schema; chain will generate 'query' internally
        result = chain.invoke({
            "question": request.question,
        })

        # Extract intermediate steps
        intermediate_steps = result.get("intermediate_steps", [])
        cypher_query = intermediate_steps[0]["query"] if len(intermediate_steps) > 0 else ""
        database_results = intermediate_steps[1]["context"] if len(intermediate_steps) > 1 else ""
        answer = result.get("result", "")

        # Save to chat history
        chat_history.append({
            "question": request.question,
            "answer": answer,
            "cypher": cypher_query,
            "db_results": database_results
        })

        return {
            "answer": answer,
            "cypher_query": cypher_query,
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))