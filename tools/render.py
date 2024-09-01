import sys
from pathlib import Path

import bpy
import numpy as np


# pylint: disable=too-many-locals
def render_paired_images(
    object_path: Path,
    output_dir: Path,
    distance_between_cameras: float = 5.0,
    distance_from_object: float = 15.0,
):
    """
    Render object and save paired images.

    Parameters
    ----------
    object_path : str
        Path to .obj file for rendering.
    output_dir : str
        Path to save directory for rendered images.
    distance_between_cameras : float
        Distance between cameras to create to create paired images.
    distance_from_object : float
        Distance from render object.

    """
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the OBJ file
    bpy.ops.import_scene.obj(filepath=object_path.as_posix())

    # Center the object and adjust scale
    obj = bpy.context.selected_objects[0]  # Assuming only one object is imported
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0, 0, 0)
    obj.scale = (1, 1, 1)

    # Set up two cameras
    distance_between_cameras /= 2  # Position cameras symmetrically
    camera1_data = bpy.data.cameras.new(name="Camera1")
    camera1_object = bpy.data.objects.new("Camera1", camera1_data)
    camera2_data = bpy.data.cameras.new(name="Camera2")
    camera2_object = bpy.data.objects.new("Camera2", camera2_data)

    bpy.context.scene.collection.objects.link(camera1_object)
    bpy.context.scene.collection.objects.link(camera2_object)

    # Position the cameras
    camera_angles = np.deg2rad(
        [
            63 + np.random.uniform(-5, 5),
            0,
            45,
        ]
    )  # TODO: hardcode, move to arguments

    base_location = (
        np.array([np.sin(camera_angles[2]), -np.cos(camera_angles[2]), np.cos(camera_angles[0])])
        * distance_from_object
        * np.random.uniform(0.8, 1.2)
    )

    step_shift = np.array([np.sqrt(2) / 2, np.sqrt(2) / 2, 0]) * distance_between_cameras * np.random.uniform(0.8, 1.2)

    camera1_object.location = tuple(base_location + step_shift)
    camera2_object.location = tuple(base_location - step_shift)

    camera_rotation = tuple(camera_angles.tolist())
    camera1_object.rotation_euler = camera_rotation
    camera2_object.rotation_euler = camera_rotation

    # Set up a light source
    light_data = bpy.data.lights.new(name="Light", type="POINT")
    light_object = bpy.data.objects.new(name="Light", object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = (12, -8, 10)  # TODO: hardcode
    light_data.energy = 2000  # Increase light intensity

    # Ensure a world background exists and set its color
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    bpy.context.scene.world.color = (0.05, 0.05, 0.05)  # Dark gray

    # Apply a basic material to ensure the object is visible
    mat = bpy.data.materials.new(name="Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get("Principled BSDF")
    principled_bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)  # Light gray
    obj.data.materials.append(mat)

    # Set rendering engine and resolution
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080  # TODO: hardcode, move to arguments

    # Render images from both cameras
    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True, parents=True)

    # Render from Camera 1
    bpy.context.scene.camera = camera1_object
    bpy.context.scene.render.filepath = (output_dir / f"{object_path.stem}_1.png").as_posix()
    bpy.ops.render.render(write_still=True)

    # Render from Camera 2
    bpy.context.scene.camera = camera2_object
    bpy.context.scene.render.filepath = (output_dir / f"{object_path.stem}_2.png").as_posix()
    bpy.ops.render.render(write_still=True)


def main():
    np.random.seed(42)
    argv = sys.argv[sys.argv.index("--") + 1 :]

    for i in range(10):  # TODO: hardcode, move to arguments
        render_paired_images(
            object_path=Path(argv[0]),
            output_dir=Path(argv[1]) / f"pair_{i}",
            distance_between_cameras=float(argv[2]),
            distance_from_object=float(argv[3]),
        )


if __name__ == "__main__":
    main()
