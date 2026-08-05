# `demo/`

A standalone Gradio demo (`app.py`) built on `translate_psa.py`, a
model-priority inference module: fine-tuned NLLB first, mT5 per-direction
second, mT5 combined third. Separate from `notebooks/PSA_Translate_FromDriveToAnyone.ipynb`
(repo root's Google-Drive-hosted demo) and from `ekegusii_internal/llm_dict_prompt/streamlit_app.py`
(the dictionary-prompted approach's own demo, in a different, private folder).

## Running it

```bash
pip install -r requirements-deploy.txt
python app.py
```

`requirements-deploy.txt` is the minimal set for running the demo only —
training dependencies (mlflow, accelerate, datasets, unbabel-comet) live in
`../notebooks/full_pipeline/requirements.txt` instead and aren't needed here.

## Model checkpoints required, not included

`app.py`/`translate_psa.py` load fine-tuned checkpoints from
`PSA-MT-Outputs/models/fine_tuned/mt5/` and
`PSA-MT-Outputs-v2/models/fine_tuned/nllb/`, relative to wherever this is
run. These are real trained weights (multiple GB) and are not committed to
this repo. Produce them by running the notebooks in
`../notebooks/full_pipeline/`, or point the path constants near the top of
each script at your own checkpoint directory.
