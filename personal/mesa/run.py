from typing import Any, Dict, List, Tuple
from pathlib import Path
import argparse
import json
import numpy as np
from lib.datagen.utils import make_openrouter_pi
from personal.mesa.model import OpinionModel
from scipy.spatial.distance import pdist, squareform

def parse_personas(path : Path) -> List[str]:
  """Load personas from a JSON file
  
  Args:
      path (Path):"""
  with open(path) as f:
    data = json.load(f)
  personas = [d["persona"] if isinstance(d, dict) else d for d in data]
  return personas

def parse_embeddings(path : Path) -> List[List[float]]:
  """Load 10 pca embeddings from a JSON file
  
  Args:
      path (Path):"""
  with open(path) as f:
    data = json.load(f)
  embeddings = [d["embedding_pca10"] if isinstance(d, dict) else d for d in data]
  return embeddings

def make_interaction_matrix(embeddings: List[List[float]]) -> np.ndarray:
  """Builds an interaction matrix based on 10 pca embeddings
  
  Args:
    embeddings (List[List[float]]):"""
  metric = 'cosine'
  X = np.array(embeddings)
  distance = pdist(X, metric=metric)
  similarity = 1 - distance
  discrete_similarity = np.where(
      similarity < -1/3, -1,
      np.where(similarity > 1/3, 1, 0)
  )
  return squareform(discrete_similarity)

def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--mode", choices=("subjective", "objective"),
          default="subjective",
          help="subjective -> AGREE/DISAGREE; objective -> answer A/B.")
  parser.add_argument("--model", default="nvidia/nemotron-3-ultra-550b-a55b:free")
  parser.add_argument("--temperature", default="0.2")
  parser.add_argument("--iterations", type=int, default="6")
  args = parser.parse_args()

  data_dir = "data/subj" if args.mode == "subjective" else "data/obj"
  personas = parse_personas(f"{data_dir}/personas.json")
  embeddings = parse_embeddings(f"{data_dir}/personas.json")

  subj_question = "Racism is bad."

  obj_question = "0 is a natural number."
  obj_choices = {
    "A": "True",
    "B": "False",
  }

  J = make_interaction_matrix(embeddings)

  pi = make_openrouter_pi(
    model=args.model,
    temperature=args.temperature,
    max_output_tokens=512,
    extra_body={
      "reasoning": {
        "effort": "none",
        "max_tokens": 64,
        "exclude": False,
      },
      "provider": {
        "options": {
          "chat_template_kwargs": {
            "enable_thinking": False
          } 
        }
      }
    }
  )

  timesteps = args.iterations
  mesa_model = OpinionModel(personas[:8], 
                            obj_question, 
                            J,
                            pi,
                            timesteps,
                            mode=args.mode,
                            choices=obj_choices
                            )

  mesa_model.run()

if __name__ == "__main__":
  main()