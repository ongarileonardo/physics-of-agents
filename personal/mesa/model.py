from lib.datagen.utils import Pi
from typing import Optional
import mesa 
import LLMService
import agents
import numpy as np

class OpinionModel(mesa.Model):
  """A model of LLM-driven agents"""

  def __init__(
    self,
    personas: list[str],
    question: str,
    J: np.ndarray,
    pi: Pi,
    *,
    name: str = "replica_0",
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

    self.llm = LLMService(pi=pi)
    self.agents = [
      agents.OpinionAgent(
        model=self,
        agent_index=i,
        persona=persona,
      ) for i, persona in enumerate(personas)
    ]
    self.round = 0

  def distribute_messages(self):
    for agent in self.agents:
      i = agent.agent_index
      message = agent.message_history[-1]
      for other_agent in self.agents:
        j = other_agent.agent_index
        if self.J[i, j] > 0:
          other_agent.receive_message(message, agree=True)
        elif self.J[i, j] < 0:
          other_agent.receive_message(message, agree=False)

  def step(self):
    agents = self.agents

    # phase A: communication 

    messages = self.llm.run_concurrent(
      task=lambda agent: agent.generate_message(),
      agents=agents,
    )

    for agent, message in zip(agents, messages):
      agent.message_history.append(message)

    self.distribute_messages()

    # phase B: opinion update

    self.llm.run_concurrent(
      task=lambda agent: agent.sample_spin(k=self.k),
      agents=agents,
    )

    self.round += 1