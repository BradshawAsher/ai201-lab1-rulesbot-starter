# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
Build a compact context block with one labeled entry per chunk, kept in ranked order.

Each entry should include:
- the game name
- the distance score
- the chunk text itself

Separate entries with a clear delimiter like `---` so the model can distinguish sources quickly. Keep the game name in every entry label so the answer can be attributed cleanly, and include the distance score for transparency when deciding whether a chunk is relevant enough to trust.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are RulesBot. Answer only using the retrieved rule excerpts provided in the context. Do not use outside knowledge, do not guess, and do not fill in missing details from memory. If the context does not contain the answer, say that the answer is not found in the loaded rules.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
Always name the game or games the answer comes from. If the answer uses more than one excerpt, mention every relevant game. If the answer is not found, say that clearly instead of inventing a citation.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
I couldn't find anything relevant in the loaded rule books. Try rephrasing your question — or check that your ingestion pipeline is working.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Filter out chunks with distance above a weak-relevance threshold before building the prompt, using the system-design guidance that cosine distances above about 0.5 are usually not trustworthy for this model.

This improves grounding and reduces hallucinations because the LLM sees fewer weak matches. The tradeoff is that an unusual paraphrase may get filtered out even when it is technically useful, so if every chunk is above the threshold the safest response is the fallback instead of forcing an answer.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
The system message will contain the grounding and citation instructions, plus the rule that the model must answer only from the provided context and use the fallback when the answer is missing.

The user message will contain the original question and the formatted retrieved context block. The user message should not add extra guidance beyond the query and the excerpts, so the model has one clear task: answer the question from the supplied rules.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: [to be completed after implementing generate_response()]
Response: [to be completed after implementing generate_response()]
Correctly grounded? [to be determined]
Cited the right game? [to be determined]
```

**One thing you changed from your original spec after seeing the actual output:**

```
To be completed after implementation and testing.
```
