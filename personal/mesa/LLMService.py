from lib.datagen.utils import Pi
from concurrent.futures import ThreadPoolExecutor

class LLMService:
  """Shared LLM service for concurrent agent queries."""

  def __init__(
    self,
    pi: Pi,
    max_workers: int = 32,
  ):
    self.pi = pi
    self.executor = ThreadPoolExecutor(max_workers=max_workers)

  def run_concurrent(self, task, agents):
    futures = [
      self.executor.submit(task, agent) for agent in agents
    ]

    return [future.result() for future in futures]

  def close(self):
    self.executor.shutdown(wait=True)
