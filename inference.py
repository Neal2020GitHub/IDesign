from IDesign import IDesign
import os
import time


output_dir = f"output/{time.strftime('%Y%m%d_%H%M%S')}"
os.makedirs(output_dir, exist_ok=True)


# TODO: Change the prompt!
prompt = "A fancy bedroom"
with open(f"{output_dir}/prompt.txt", "w") as f:
    f.write(prompt)


# TODO: Change the number of objects and room dimensions!
i_design = IDesign(no_of_objects = 10,  # 15
                   user_input = prompt, 
                   room_dimensions = [4.0, 4.0, 2.5])


# import ipdb; ipdb.set_trace()
# Interior Designer, Interior Architect and Engineer 
i_design.create_initial_design()
# Layout Corrector
i_design.correct_design()
# Layout Refiner
i_design.refine_design(verbose=True)
# Backtracking Algorithm
i_design.create_object_clusters(verbose=True)
i_design.backtrack(output_dir, verbose=True)
i_design.to_json(output_dir)
