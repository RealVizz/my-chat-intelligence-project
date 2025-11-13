from message_api.utils import llm_utils

def process_user_query(question: str):
    llm_answer = llm_utils.get_llm_response(prompt=question)
    return llm_answer
