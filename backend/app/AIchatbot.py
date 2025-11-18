# backend/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from backend.qiskit_utils import run_circuit  # your existing Qiskit code

app = FastAPI()

# Allow frontend access (update in production with your frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body
class Question(BaseModel):
    question: str

# LangChain setup
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
template = """
You are a quantum computing assistant.
If the user question requires simulation, call run_circuit() using the provided data.

Question: {question}

Answer in a clear, beginner-friendly way.
"""
prompt = PromptTemplate(input_variables=["question"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

@app.post("/ask")
async def ask_question(data: Question):
    question_text = data.question.lower()

    # Simple heuristic: if user asks about circuits or simulations, run Qiskit
    if any(word in question_text for word in ["simulate", "circuit", "gate", "qubit"]):
        # Example: run a sample circuit (customize as needed)
        circuit_result = run_circuit(
            num_qubits=2,
            gates=[
                {"type": "h", "qubit": 0},
                {"type": "cx", "qubit": 0, "targets": [1]},
            ],
            shots=1024
        )
        answer = chain.run(question=f"{data.question}\nSimulation output: {circuit_result}")
    else:
        answer = chain.run(question=data.question)

    return {"answer": answer}
