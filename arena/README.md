# EM Arena

Libem-arena is a simple web service that support arena for a "game" for entity matching over a web page.

Two entities are given, and the user has to decide if they are the same or not by clicking yes or no button.
- Pairs of entities are sampled from the datasets on different topics.
- Each session contains configurable amount of pairs (default 5).

The result is compared to the ground-truth, and the user is given a score (F1) and compare to Libem.
