import os
import sqlite3
import re
from langchain_community.llms import Together
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils import load_training_data, connect_db, run_query

# === Set Together.ai API key ===
os.environ["TOGETHER_API_KEY"] = "700e2d938b084fca68a3b263033f95654f6b62d640ed10ec35d6c869f0202380"  # Replace with actual key

# === Connect to DB ===
conn = connect_db()
cursor = conn.cursor()

# === Use Together's hosted model (e.g., Mistral) ===
llm = Together(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.3,
    max_tokens=512
)

# === Schema Description (replace this with actual schema) ===
schema_description = """..."""  # TODO: Paste your Chinook schema here

# === Few-shot training examples ===
training_examples = load_training_data()

# === Prompt Template ===
template = """{schema}

{examples}

Q: {question}
A:"""

prompt = PromptTemplate(
    input_variables=["schema", "examples", "question"],
    template=template,
)

llm_chain = LLMChain(llm=llm, prompt=prompt)

# === SQL Extraction Helper ===
def extract_sql(text: str) -> str:
    match = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"(SELECT|INSERT|UPDATE|DELETE).*?;", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(0).strip()
    return text.strip()

# === Main QA Function ===
def ask_question(q: str):
    response = llm_chain.invoke({
    "schema": schema_description,
    "examples": training_examples,
    "question": q
    })

# Ensure we extract the text correctly
    if isinstance(response, dict) and "text" in response:
        result = response["text"]
    else:
        result = str(response)

    sql = extract_sql(result)

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(f"\n💻 SQL:\n{sql}")
        print(f"\n📊 Result:")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"\n❌ Error executing query: {e}")

# === CLI Loop ===
if __name__ == "__main__":
    print("💬 Ask me anything about the Chinook database! Type 'exit' to quit.")
    while True:
        question = input("\nYou: ")
        if question.lower() in ["exit", "quit"]:
            break
        ask_question(question)
