import mesa

from typing import Optional

from lib.datagen.samplers import message_sampler, \
          spin_sampler_stateful, spin_sampler

class OpinionAgent(mesa.Agent):
  """An LLM-driven agent with a persona and opinion."""

  def __init__(
    self,
    model: mesa.Model,
    agent_index: int,
    persona: str,
  ):
    super().__init__(model)

    self.agent_index = agent_index
    self.persona = persona

    self.spin = 0
    self.raw_spins: list[int] = []

    self.inbox_agree: list[str] = []
    self.inbox_disagree: list[str] = []

    self.spin_history: list[int] = []
    self.message_history: list[str] = []

  def sample_spin(self, k: int) -> int:
    spins = []
    for i in range(k):
      new_spin = spin_sampler_stateful(
        persona=self.persona,
        question=self.model.question,
        messages_agree=self.inbox_agree,
        messages_disagree=self.inbox_disagree,
        pi=self.model.llm.pi,
        current_spin=self.spin,
        mode=self.model.mode,
        choices=self.model.choices,
      )
      spins.append(new_spin)
      self.raw_spins.append(new_spin)

    if k>1:
      majority_spin = max(set(spins), key=spins.count)
    else:
      majority_spin = new_spin

    self.spin = majority_spin
    self.spin_history.append(majority_spin)

    return majority_spin

  def generate_message(self) -> str:
    """Generate a message based on the current opinion."""

    message = message_sampler(
      persona=self.persona,
      question=self.model.question,
      messages_agree=self.inbox_agree,
      messages_disagree=self.inbox_disagree,
      current_spin=self.spin,
      pi=self.model.llm.pi,
      mode=self.model.mode,
      choices=self.model.choices,
    )

    return message
  
  def receive_message(
    self,
    message: str,
    agrees: bool,
  ):
    """Receive a message in the appropriate inbox."""

    if agrees:
        self.inbox_agree.append(message)
    else:
        self.inbox_disagree.append(message)