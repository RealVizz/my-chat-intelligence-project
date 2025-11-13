ENTITY_RESOLUTION_PROMPT = """
You are an entity selection engine.
Your task is to select the most probable name from the Candidate Names list that matches the User Query.

Candidate Names:
{candidates_str}

Chat History:
{history_str}

User Query:
"{question}"

Task:
1. Analyze the User Query.
2. Compare it against the Candidate Names.
3. Ignore any names in the Chat History that do not appear in the Candidate Names list.
4. If Candidate Names list is empty, refer to chat history for a probable name.
4. Put weightage to history timeline, latest messages comes at the end and have higher weightage.
5. Account for typos (e.g., 'Cava Lli' matches 'Cavalli').

Question:
Out of the Candidate Names list provided above, which is the most probable name the user is referring to? 
Return ONLY the name. 
If absolutely no match exists, return 'None'.
"""