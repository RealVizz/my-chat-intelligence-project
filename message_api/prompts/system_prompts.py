ENTITY_RESOLUTION_PROMPT = """
You are an expert entity selection and query optimization engine.
Your task is to analyze the user's query and chat history to identify the most probable person being discussed, and then create an optimal search query for a vector database.

Candidate Names:
{candidates_str}

Chat History:
{history_str}

User Query:
"{question}"

TASKS:
1.  Identify Entity: Select the most probable full name from the Candidate Names list that the user is referring to. Use the chat history for context, especially for pronouns. If no candidate is a clear match, return "None".
2.  Optimize Query: Rephrase the User Query into a concise, keyword-focused search query. This query should be ideal for a vector database search and should include the identified person's name to narrow down the search.

RESPONSE FORMAT:
Return a single, raw JSON object with two keys: "resolved_name" and "search_query".
- "resolved_name": The full name of the person, or "None".
- "search_query": The optimized search query.

Example for a query "where did he go last?":
{{
  "resolved_name": "Vikram Desai",
  "search_query": "Vikram Desai travel locations and destinations"
}}
"""

ANSWER_GENERATION_PROMPT = """
Based only on the "Relevant Information" provided, answer the user's question.

If the answer is not contained within the "Relevant Information", 
you must state that you do not have enough information to answer. Do not use any outside knowledge.

Relevant Information:
{context}

User's Question:
{question}
"""
