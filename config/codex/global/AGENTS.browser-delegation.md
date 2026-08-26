## Browser delegation

`chrome_pilot` is for interactive control of the user's existing Chrome profile, not web search, web research, or opening public documentation. When that interactive control is actually needed, consider delegating a bounded segment to the lower-cost `chrome_pilot` custom subagent.

Keep simple browser interactions in the current agent.

When delegating, give `chrome_pilot` the requested outcome, relevant starting tab or URL, authorization boundaries, and stop condition. Then use its result to continue the task.
