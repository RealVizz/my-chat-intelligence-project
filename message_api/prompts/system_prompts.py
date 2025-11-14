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
3. If the Chat History is empty, base your decision solely on the User Query and the Candidate Names.
4. If the Chat History is NOT empty, use it to understand context, especially for pronouns (he, she, they).
5. Put weightage on the history timeline; latest messages appear at the end and have higher weightage.
6. Account for typos (e.g., 'Cava Lli' matches 'Cavalli').

Question:
Out of the Candidate Names list provided above, which is the most probable name the user is referring to? 
Return ONLY the name. 
If absolutely no match exists, return 'None'.
"""
