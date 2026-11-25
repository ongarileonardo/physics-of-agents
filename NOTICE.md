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

### 3. Non-symmetric interactions $( J )$

With simple examples, we compared the same model with a fixed, non-symmetric interaction matrix, slightly different from the symmetric **J0** used in many replicas.

The results showed that agents behave more intermittently in the non-symmetric case, but this was just a preliminary test.

### 4. Hopfield model for personas and interactions

**Theoretical concept:**
The idea is to use some feature vectors $\xi_i$ for each agent to build the interaction matrix between them.
The original idea was to force $$\xi_{i,k} \in \{0,1\}$$ and compute $$J_{ij} = \xi_i \cdot \xi_j = \sum_{k=0}^K \xi_{i,k} \ \xi_{j,k}$$

**Literature:**

_"The Dissemination of Culture: A Model with Local Convergence and Global Polarization" - Axelrod (1997)_
Axelrod proposes a simple model showing that local interactions can produce local consensus while preserving large-scale cultural diversity.
The basic model considers a population of agents, each of them with a cultural state represented by a vector of features $$\sigma_i = \{\sigma_{i,k}\}_{k=0}^F$$, where $$\sigma_{i,k} \in C \subset \mathbb{N}$$ 
Here, two agents interact with probability equal to their cultural similarity and interactions between agents increase their similarity. The surprising result found are patterns of local convergence and global polarization. The degree of cultural similarity between two individuals is defined as the percentage of their features that have the identical trait. For example, if two agents share two of the five attributes, their cultural similarity is 40%.

\
\
_"An agent based force vector model of social influence that predicts strong polarization in a connected world" - G. Jordan Maclay and Moody Ahmad (2021)_
In this paper, an agent is represented as a two-dimensional vector, that represents the attribute space $$A_i = (x_i, y_i)$$ Here, $x$ and $y$ are attributes like social and economic condition.
The authors introduce a force between two agents inspired by gravitational and electric dipole interactions.

\
\
_"Hopfield and Hebbian Models of Belief Polarization: Neural Networks, Social Contexts" - Graham Sack, Carissa Flocke (2013)_
Unlike Axelrod, this paper introduces signed social networks instead of probability of interactions. The setup is very similar to "Physics of Agents" paper.

\
**Implementation:**
In `data/subj/personas.json` and `data/obj/personas.json` are stored personas descriptions and their corresponding 10 PCA embedding, although there is no official documentation on their generation.

Based on this embedding, different measures were tested to compute similarity between personas. The corresponding notebook is `analysis/personas_similarity.ipynb`