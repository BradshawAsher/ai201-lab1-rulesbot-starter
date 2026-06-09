from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)
_RELEVANCE_THRESHOLD = 0.5


_FALLBACK_RESPONSE = (
    "I couldn't find anything relevant in the loaded rule books. "
    "Try rephrasing your question — or check that your ingestion pipeline is working."
)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return _FALLBACK_RESPONSE

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("distance", 1.0) <= _RELEVANCE_THRESHOLD
    ]

    if not relevant_chunks:
        return _FALLBACK_RESPONSE

    context_blocks = []
    for chunk in relevant_chunks:
        context_blocks.append(
            "Game: {game}\nDistance: {distance:.3f}\nText: {text}".format(
                game=chunk.get("game", "Unknown"),
                distance=chunk.get("distance", 1.0),
                text=chunk.get("text", ""),
            )
        )

    system_message = (
        "You are RulesBot. Answer only using the retrieved rule excerpts provided in the context. "
        "Do not use outside knowledge, do not guess, and do not fill in missing details from memory. "
        "If the context does not contain the answer, say that the answer is not found in the loaded rules. "
        "Always name the game or games the answer comes from. If the answer uses more than one excerpt, "
        "mention every relevant game. If the answer is not found, say that clearly instead of inventing a citation."
    )

    user_message = (
        f"Question: {query}\n\n"
        "Retrieved rule excerpts:\n"
        f"{'\n---\n'.join(context_blocks)}"
    )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content
    if content is None:
        return _FALLBACK_RESPONSE

    content = content.strip()
    return content if content else _FALLBACK_RESPONSE
