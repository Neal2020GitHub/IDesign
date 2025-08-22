# IDesign
This is the official Github Repo for [*I-Design: Personalized LLM Interior Designer*](https://atcelen.github.io/I-Design/)

## Requirements
Install the requirements
```bash
conda create -n i-design python=3.10
conda activate i-design
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
pip install -U git+https://github.com/NVIDIA/MinkowskiEngine --no-deps
conda install -c dglteam/label/th24_cu118 dgl
```
Create the "OAI_CONFIG_LIST.json" file
```json
[
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-4-1106-preview",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-3.5-turbo-1106",
        "api_key": "YOUR_API_KEY",
        "api_version": "2023-03-01-preview"
    }
]
```
## Inference
Create the scene graph and allocate coordinate positions
```bash
python test.py
```

Retrieve the 3D assets from Objaverse using OpenShape
```bash
git clone https://huggingface.co/OpenShape/openshape-demo-support
cd openshape-demo-support
pip install -e .
```
```bash
python retrieve.py --output_dir output/20250821_094436
```

Place the assets using the Blender Scripting Module
```bash
python place_in_blender.py --output_dir output/20250821_094436
```

## Evaluation
After creating scene renders in Blender, you can use the GPT-V evaluator to generate grades for evaluation. Fill in the necessary variables denoted with TODO and run the script
```bash
python gpt_v_as_evaluator.py
```

## Results
![gallery](imgs/gallery.jpg)
