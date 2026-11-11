# NOTICE

## Original code

This project is based on code originally distributed under the Apache License, Version 2.0.

The original license is available in the [`LICENSE`](LICENSE) file.

## Modifications

The original implementation has been adapted and extended.

### 1. Mesa

Mesa is an Apache2 licensed agent-based modeling framework in Python that allows users to quickly create agent-based models using built-in core components and analyze their results using Python’s data analysis tools.

The idea is to replace the current implementation (raw Python code) with a formal model using Mesa. To do so, a new folder has been created (`personal/mesa/`), with a Jupyter Notebook that recreates the environment using `mesa.Agent` and `mesa.Model` classes. The notebook provides also code for visualization, although it is designed for a small number of agent.

Results are stored under `personal/mesa/pdf`, ignored by git on purpose.

### 2. Stateful Spin Sampler

The original implementation deliberately adopts a stateless approach to opinion sampling: at time step $(t)$, an agent's new opinion is sampled without explicitly conditioning on its previous opinion at time step $(t-1)$. Consequently, the Markovian assumption underlying the update mechanism is challenged.

A new (stateful) sampler has been added, designed to provide previous opinion context during spin sampling. After a quick comparison, in the stateful model agents are less incline to change opinion.

More generally, the agents used in this project do not maintain an explicit, persistent internal state. However, the ability to maintain an internal state is a fundamental characteristic of an agent: an LLM alone, without additional mechanisms for maintaining state, memory, and context, cannot be considered a fully-fledged agent. The Mesa framework could help address this limitation by providing an agent-oriented architecture in which persistent state variables can be explicitly defined and maintained across simulation steps.

### 3. Future Work
- Non-symmetric interactions $( J )$
- Hopfield model for defining personas and interactions