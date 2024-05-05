# Libem Tune

input --> libem --> pred vs. label -> F1 or other speed / token cost

tune.py
- collect a "parameter tree" from the modules ("Parameters")
- node: representing a module / the module's parameters (parameter.py and prompt.py)
- edge: dependency between modules (e.g., libem -> match -> browse, libem -> prepare) # why dependency?
- "Parameters" contains all parameters in the "program"
- We want to do a search over the "Parameters" to figure out the optimal one given training data
- E.g., grid search, which linearly go through each parameter without revisiting ...
- "Parameters".export() -> optimal

tune loop:
- sample parameters according to the search policy, which gives a parameter vector at each iteration
- set the parameters using the vector to all modules (e.g., match, prepare, browse)
- inner loop for each record:
  - call libem.match(left, right) -> pred, get s = score(pred, label)
- get array of param vec -> scores
- optimal params = argmax vec -> store it in "Parameters" where each node.optimal keeps the optimal value there.

How to support localized tune? Feel an advanced version.
- Broswer score -> cosine similarity # if the result is obvious bad, we can tune it
- Prepare score -> cosine (?)
