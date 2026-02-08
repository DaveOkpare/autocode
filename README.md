User provides details    -->      Planning Agent 
             ↑           (no)            ↓
  Asks followup question <--  Understands the query
                                         ↓
                            Generates project specifications 
                            (stack, tests, features, db schema,
                            api endpoint, implementation steps etc.)
                                         ↓
           --> new context window --> Coding Agent --> (recursively works and updates feature list)
           ↑                                                            ↓ 
(use context from previous                                              ↓
    implementation)                                                     ↓
           ↑                                                            ↓
(update memory with failure,   (tests previous implementation           ↓
bugs and solutions)      <--      before starting new feature)       <--


Planning agent should have a tool to write a plan to file or ask clarifying questions. 
The file should be the `features.json` file in the `projectDir`. 
So we can use deferred tool call (human in the loop) to ask clarifying questions. 
The output of the planning step will then be stored at `projectDir/features.json`.

We can as well use deferred tool call (human in the loop) to confirm the plan before writing the final implementation plan. Tool call will contain a specification of the plan. Then when confirmed or new details are provided, the plan will be updated accordingly.

When plan is confirmed, then we return BaseModel of the final implementation plan which would then be stored at `projectDir/features.json`.

Coding agent should be aware of the context window it is working with. 
At the start of a conversation, the agent receives information about its total context window:

`<budget:token_budget>200000</budget:token_budget>`

After each tool call, the agent receives an update on remaining capacity:

`<system_warning>Token usage: 35000/200000; 165000 remaining</system_warning>`

When the model is approaching the context window limit, it should consider committing its current work and update the progress log. Update feature_list.json if tests verified, ensure no uncommitted changes, leave app in working state (no broken features). Return `response: str, status: str[continue|error]`

* how to stop agent *

- when max_iterations is reached
- checking the remaining features. 
- when exception occurs

```
passing, total = count_passing_tests(project_dir)
  if passing == total and total > 0:
      print("\n🎉 All tests passing!")
      break
```

* how to run infinite loop *

- try/except (return exception as string rather than breaking)
- new context window restarts exploration
- errors are logged, not passed to the next iteration

* how to use memory tool *

- memory tool is kinda like a knowledge base that can be used to store and retrieve information.
- use it after solving a bug, that way we can reuse the solution later.
- i'm also thinking of using it to store progress especially when the agent is approaching the context window limit.
- when an incomplete process was logged in memory, it should be cleared after the process is completed.
