---
trigger: model_decision
---

When answering user on chat to write code (develop), enhance, refactor or fix bugs, consider the following points to include in the response :

**always** :
  - use cases clarification : even in a success response, if there is information that could improve the last response to be include (more or missing ) :
    - use cases
    - logic rules
    - exepected behaviors
    - etc...
Write and add a small summary in markdown of what you already know now, suggesting the missing ones to be added, to help user learn, confirm, extend or add the expected information.


**only when needed** :
  - use cases clarification : if there is a need to be more clear in the use cases, logic rules or exepected behaviors, write a summary in markdown of what you know now, so user can confirm, extend or add the expected information.
  - bugs after failed attempt to fix: after failing to fix a bug in one shot, offer new strategies to test, refactor or isolate functionality to aid fixing the bug as needed

