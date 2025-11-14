from datetime import datetime, timezone

from rapidfuzz import process

from message_api.prompts import system_prompts
from message_api.schemas import ChatMessageSchemaObj
from message_api.utils import llm_utils, db_utils, rag_utils

_chat_history: list[ChatMessageSchemaObj] = []
_identities_cache: list[str] = []


def load_history_on_startup():
    """Loads chat history from DB into the in-memory cache."""
    global _chat_history
    history_from_db = db_utils.load_chat_history()
    _chat_history = [ChatMessageSchemaObj(**msg) for msg in history_from_db]
    # print(f"Loaded {_chat_history.__len__()} messages from chat history.")


def load_identities_on_startup():
    """Loads unique identity names from DB into the in-memory cache."""
    global _identities_cache
    _identities_cache = db_utils.load_unique_identities()
    # print(f"Loaded {_identities_cache.__len__()} unique identities into cache.")


def _add_turn_to_history(user_content: str, assistant_content: str):
    """Adds a full user/assistant turn to the history and database."""
    now_utc = datetime.now(timezone.utc)

    db_utils.add_message_to_chat_history(role="user", content=user_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="user", content=user_content, timestamp=now_utc))

    db_utils.add_message_to_chat_history(role="assistant", content=assistant_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="assistant", content=assistant_content, timestamp=now_utc))


def _find_potential_identity_matches(question: str):
    """Uses fuzzy matching to find the top 5 potential identity matches."""
    potential_matches = process.extract(question, _identities_cache, score_cutoff=45.0, limit=5)
    print([match[0] for match in potential_matches])
    return [match[0] for match in potential_matches]


def _identify_subject_of_query(question: str, history: list[ChatMessageSchemaObj], candidates: list[str]):
    """Uses an LLM call to determine the subject of the user's query from a list of candidates."""
    if not candidates:
        return None

    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-10:]])
    candidates_str = ", ".join(candidates)

    prompt = system_prompts.ENTITY_RESOLUTION_PROMPT.format(
        history_str=history_str,
        candidates_str=candidates_str,
        question=question
    )

    llm_response = llm_utils.get_llm_response(messages=[{"role": "user", "content": prompt}])

    if llm_response and llm_response.strip() != "None":
        if llm_response.strip() in candidates:
            return llm_response.strip()
    return None


def _prepare_context_from_retrieved_docs(docs: list[dict]):
    """Formats the retrieved documents into a string context for the LLM."""
    if not docs:
        return "No relevant information found in the knowledge base."

    context_str = "Relevant Information:\n"
    for doc in docs:
        context_str += f"- From {doc.get('user_name', 'Unknown')}: '{doc.get('message', '')}'\n"
    return context_str


def _resolve_entity(question: str) -> str | None:
    """Encapsulates the 'Who' step: resolves the entity from the user's question."""
    potential_matches = _find_potential_identity_matches(question)

    resolved_identity = _identify_subject_of_query(
        question=question,
        history=_chat_history,
        candidates=potential_matches
    )

    if resolved_identity:
        print(f"--- Entity Resolution: LLM identified '{resolved_identity}' ---")
    else:
        print("--- Entity Resolution: LLM could not identify a subject. ---")

    return resolved_identity


def _filter_and_search_documents(question: str, resolved_identity: str | None) -> str:
    """Encapsulates the 'Filter' and 'Search' steps: retrieves relevant context."""
    filter_ids = None
    if resolved_identity:
        filter_ids = db_utils.get_message_ids_by_user_name(resolved_identity)
    else:
        print("--- Searching all documents as no specific entity was resolved. ---")

    relevant_doc_ids = rag_utils.find_relevant_documents(query=question, filter_ids=filter_ids)
    retrieved_docs = db_utils.get_raw_messages_by_ids(relevant_doc_ids)
    context = _prepare_context_from_retrieved_docs(retrieved_docs)
    return context


def _generate_answer(question: str, context: str) -> str:
    """Encapsulates the 'Answer' step: generates the LLM's response."""
    messages_for_llm = [msg.model_dump(exclude={'timestamp'}) for msg in _chat_history]
    question_with_context = f"Context:\n{context}\n\nQuestion: {question}"
    messages_for_llm.append({"role": "user", "content": question_with_context})
    llm_answer = llm_utils.get_llm_response(messages=messages_for_llm, provider="gemini")
    return llm_answer


def process_user_query(question: str):
    """Processes a user query using the full RAG pipeline."""
    resolved_identity = _resolve_entity(question)  # 1: "Who" - Entity Resolution.
    context = _filter_and_search_documents(question, resolved_identity)  # 2: "Filter" & "Search" - Retrieval.
    llm_answer = _generate_answer(question, context) # 3: "Answer" - Generation.

    if llm_answer:  # Step 4: History
        _add_turn_to_history(user_content=question, assistant_content=llm_answer)

    return llm_answer
