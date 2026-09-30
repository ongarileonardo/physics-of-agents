## Personal notes

Instructions for running data generation: For generating the data, use the files under lib/. The following command will use the first question (``--limit 1``) from the training and test sets for the subjective dataset (`data/subj/train.jsonl`, `data/subj/test.jsonl`). It uses the first four personas (``--num-agents 4``) from `data/subj/personas.json`, one shared graph, two update rounds, and three opinion samples per
agent. `--num-edges 6` specifies six nonzero entries in the symmetric interaction matrix, corresponding to three undirected connections. This demo uses simulated responses through the --mock option, requires no API key, and takes approximately one second on the tested machine. To generate responses using gpt-4o-mini, remove --mock and set the OPENAI_API_KEY environment variable. Runtime for API-backed generation depends on response times and rate limits. Run the following command from the repository root.

```bash
python -m lib.datagen.collect_energy \
  --mock \
  --mode subjective \
  --limit 1 \
  --num-agents 4 \
  --num-edges 6 \
  --num-train-graphs 1 \
  --num-seen-graphs 1 \
  --num-fresh-graphs 0 \
  --no-lattices \
  --trajectories 1 \
  --num-steps 2 \
  --k 3 \
  --max-workers 1 \
  --seed 0 \
  --output-dir 
```

The script will write files into the "demo_output" directory. To be able to see the results, move the files into "data/models/mock/subjective_energy", and then run the "clean_data.ipynb" notebook.

From there, it is possible to run the "0_example.ipynb" notebook to visualize the evolution of the agents'opinion over time and other interesting statistics.