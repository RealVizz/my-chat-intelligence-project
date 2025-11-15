# Exploratory Data Analysis Report

This document provides a detailed summary of the findings from the exploratory data analysis performed on the message dataset.

### API & Data Integrity

-   **API Stability:** The source API is unstable. During a full data fetch, multiple `4xx` errors were encountered (`400`, `401`, `404`, `405`). A robust fetching mechanism with retries was necessary to acquire the complete dataset.
-   **Data Integrity:** The dataset itself is clean and well-structured.
    -   **User ID Integrity:** ✅ CLEAN. Every `user_name` maps to exactly one `user_id`.
    -   **Duplicate Message IDs:** ✅ CLEAN. No duplicate message IDs were found.

---

### Dataset Statistical Overview

-   **Total Messages:** 3349
-   **Unique Users:** 10
-   **Date Range:** 2024-11-08 to 2025-11-08

---

### Behavioral and Content Analysis

#### Overall Sentiment Distribution

The sentiment of the messages is overwhelmingly neutral-to-positive, with very few negative messages. This is atypical for a real-world customer service dataset.

```
Counter({'positive': 1771, 'neutral': 1450, 'negative': 128})
```

#### Common Phrases & Keywords

N-gram analysis reveals common user intent and topics.

**Top 10 Common Phrases (Bigrams):**
```
[(('id', 'like'), 85),       # Typo for "I'd like"
 (('next', 'month'), 68),
 (('next', 'week'), 55),
 (('new', 'york'), 51),
 (('make', 'sure'), 45),
 (('arrange', 'private'), 40),
 (('dinner', 'reservation'), 38),
 (('im', 'looking'), 37),     # "I'm looking"
 (('private', 'jet'), 33),
 (('hotel', 'room'), 32)]
```

**Top 5 Common Phrases (Trigrams):**
```
[(('new', 'years', 'eve'), 14),
 (('cannes', 'film', 'festival'), 12),
 (('monaco', 'grand', 'prix'), 12),
 (('book', 'private', 'jet'), 11),
 (('arrange', 'private', 'tour'), 10)]
```

**Transactional Keyword Breakdown:**
```
[('arrange', 212),
 ('hotel', 190),
 ('tickets', 187),
 ('book', 178),
 ('reservation', 126),
 ('confirm', 112),
 ('flight', 98),
 ('yacht', 86),
 ('restaurant', 86),
 ('car', 71)]
```

---

### User Persona Analysis

A key finding is that all 10 users in the dataset are **behavioral clones**. They exhibit statistically near-identical behavior across multiple metrics, which is not representative of a real user base.

**Note on "Avg Sentiment":** The "Average Sentiment" score is calculated using VADER's compound score, which ranges from -1.0 (most negative) to +1.0 (most positive). A score around 0.2 indicates a consistently neutral-to-mildly-positive tone.

| User                   | Avg Sentiment | Question Pct. | Exclamation Pct. | Transactional Pct. |
| ---------------------- | ------------- | ------------- | ---------------- | ------------------ |
| Amina Van Den Berg     |          0.21 |         31.6% |             2.0% |              39.5% |
| Armand Dupont          |          0.23 |         34.2% |             0.9% |              40.1% |
| Fatima El-Tahir        |          0.20 |         29.5% |             1.4% |              40.1% |
| Hans Müller            |          0.24 |         35.4% |             3.5% |              35.0% |
| Layla Kawaguchi        |          0.22 |         31.2% |             2.1% |              39.4% |
| Lily O'Sullivan        |          0.24 |         31.5% |             2.7% |              38.6% |
| Lorenzo Cavalli        |          0.22 |         35.4% |             2.4% |              36.1% |
| Sophia Al-Farsi        |          0.23 |         33.2% |             3.2% |              33.8% |
| Thiago Monteiro        |          0.22 |         33.2% |             1.9% |              42.1% |
| Vikram Desai           |          0.22 |         33.4% |             2.7% |              34.9% |

---

### Preference Message Context Analysis

This analysis reveals how and when users state their preferences.

-   **Methodology:**
    1.  First, we identified all messages containing a "preference keyword" (e.g., `I prefer`, `my wife likes`, `allergic to`).
    2.  Then, within that subset of messages, we checked how many *also* contained a "transactional keyword" (e.g., `book`, `flight`, `hotel`).

-   **Finding:**
    -   **40.2%** of all preference-related messages were also transactional.

-   **Conclusion:**
    -   This is a critical insight. It means that users frequently embed their personal preferences directly within booking requests. For a real-world concierge AI, this implies that the system must not only fulfill the immediate request but also be capable of extracting and storing these preferences for future use (e.g., remembering a user's preferred airline or seating choice).
