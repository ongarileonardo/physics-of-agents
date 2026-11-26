from lib.datagen.utils import Pi
from typing import Optional, Callable
import mesa 
import numpy as np
from personal.mesa.LLMService import LLMService
from personal.mesa.agents import OpinionAgent

class OpinionModel(mesa.Model):
  """A Mesa-based agent-based model of LLM-driven agents and opinion dynamics.

  The model represents a population of agents, each characterized by a
  persona, interacting within an opinion space. Their opinions and
  interactions are governed by a coupling matrix and personal profiles.

  Args:
      personas (list[str]): List of persona descriptions defining the
          characteristics and behavior of each LLM-driven agent.
      question (str): Question or topic presented to the agents, around
          which opinions and interactions are organized.
      J (np.ndarray): Interaction or coupling matrix encoding the
          influence between agents.
      pi (Pi): Probability distribution or model component governing
          the opinion dynamics. In practice, this is a Callable object
          that returns an LLM response.
      timesteps (int): Number of communication steps.
      name (str, optional): Identifier assigned to the model instance.
          Defaults to ``"test_0"``.
      mode (str, optional): Subjective or Objective, regarding questions.
          Defaults to ``"subjective"``.
      choices (dict[str, str], optional): Mapping of possible choices
          and their descriptions, if the model operates in objective
          mode. Defaults to ``None``.
      k (int, optional): Number of sample for each individual agent at 
          a certain time. Defaults to ``1``.
      seed (int, optional): Random seed for reproducibility. Defaults
          to ``None``.

  """

  def __init__(
    self,
    personas: list[str],
    question: str,
    J: np.ndarray,
    pi: Pi,
    timesteps: int,
    *,
    name: str = "test_0",
    mode: str = "subjective",
    choices: Optional[dict[str, str]] = None,
    k: int = 1,
    seed: Optional[int] = None,
  ):
    super().__init__(seed=seed)

    self.name = name
    self.question = question
    self.J = np.asarray(J, dtype=np.int8).copy()
    self.mode = mode
    self.choices = choices
    self.timesteps = timesteps

    self.llm = LLMService(pi=pi)
    self.opinion_agents = [
      OpinionAgent(
        model=self,
        agent_index=i,
        persona=persona,
      ) for i, persona in enumerate(personas)
    ]
    self.round = 0
    self.k = k

  def distribute_messages(self):
    for agent in self.opinion_agents:
      i = agent.agent_index
      message = agent.message_history[-1]
      for other_agent in self.opinion_agents:
        j = other_agent.agent_index
        if self.J[i, j] > 0:
          print(f"- **(+) agent {i} to {j}:**\n \t - _{message}_ \n")
          other_agent.receive_message(message, agree=True)
        elif self.J[i, j] < 0:
          print(f"- **(-) agent {i} to {j}:**\n \t - _{message}_ \n")
          other_agent.receive_message(message, agree=False)

  def step(self):
    print(f"## Step {self.round}")

    agents = self.opinion_agents

    # phase A: communication 

    print("### Messages")

    messages = self.llm.run_concurrent(
      task=lambda agent: agent.generate_message(),
      agents=agents,
    )

    for agent, message in zip(agents, messages):
      agent.message_history.append(message)

    self.distribute_messages()

    # phase B: opinion update

    print("### Opinions")

    self.llm.run_concurrent(
      task=lambda agent: agent.sample_spin(k=self.k),
      agents=agents,
    )

    self.round += 1

  def run(self):
    print(f"# Question: {self.question} \n")
    for agent in self.opinion_agents:
      print(f"**Agent {agent.agent_index}**: {agent.persona} \n")

    for t in range(self.timesteps):
      self.step()