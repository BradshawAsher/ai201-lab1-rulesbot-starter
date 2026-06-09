# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I will call `_collection.query()` with `query_texts=[query]`, `n_results=n_results`, and `include=["documents", "metadatas", "distances"]`.

- `query_texts=[query]` runs one semantic search for the single user query.
- `n_results=n_results` returns up to the requested number of top matches.
- `include=["documents", "metadatas", "distances"]` gives me the raw chunk text, the stored game metadata, and the similarity score needed for ranking.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
{
  "text": "A Wild card can be played on any color and lets you choose the next color.",
  "game": "Uno",
  "distance": 0.0832
}

- `text` comes from the matching document returned by `query()`.
- `game` comes from the matching metadata returned by `query()`.
- `distance` comes from the matching distance score returned by `query()`.
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
`_collection.query()` returns one result list per query because it is designed to support batch queries.

Since we only pass a single query, we use index `[0]` to access the first (and only) result set.

For example, `results["documents"][0]`, `results["metadatas"][0]`, and `results["distances"][0]` are the actual lists of matches for our one query.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
I will return all `n_results` regardless of a hard distance threshold.

Tradeoffs:
- returning all `n_results` means the caller still gets the requested number of candidates, which is useful when the generator can decide whether context is relevant.
- filtering by a threshold can improve precision, but risks returning fewer than expected results and may hide edge-case answers when query wording is unusual.

Because this project uses retrieved chunks as grounding context, it is safer to return the top `n_results` and let the higher-level logic handle poor matches.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) If the collection is empty, the function returns `[]` immediately without querying.

(b) If the query matches no chunks well, the function still returns the top few chunks from `_collection.query()` and their distances. Higher distances mean lower relevance, so the generator can detect weak grounding if needed.

(c) If the query matches chunks from multiple games, the function returns them in ranked order by distance. The response generator can then use the best matches even if they come from different games.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: How does the spymaster give clue in codenames?
Top result game: [Codenames]
Distance score: 0.289
Does it make sense? yes
```

**One thing about the query results that surprised you:**

```
it was good it's just that chunks aren't full sentences
```
