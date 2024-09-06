import argparse
import subprocess
import sys
from pathlib import Path

import bpy
import numpy as np


# pylint: disable=too-many-locals
def render_paired_images(
    object_path: Path,
    output_dir: Path,
    object_scale: float,
    distance_between_cameras: float = 412.0,  # Updated distance between cameras
    distance_from_object: float = 639.0,  # Updated distance from center to the object
    focal_length: float = 80.0,  # Updated focal length of the camera
    resolution_x: int = 5120,  # Updated picture resolution width
    resolution_y: int = 4096,  # Updated picture resolution height
):
    """
    Render object and save paired images.

    Parameters
    ----------
    object_path : str
        Path to .stl file for rendering.
    output_dir : str
        Path to save directory for rendered images.
    object_scale : float
        Scale object size.
    distance_between_cameras : float
        Distance between cameras to create paired images.
    distance_from_object : float
        Distance from the center between the cameras to the object.
    focal_length: float
        Lens focal length in millimeters.
    resolution_x: int
        Width of the picture resolution.
    resolution_y: int
        Height of the picture resolution.

    """
    _setup_object(object_path=object_path, object_scale=object_scale)

    camera1_object, camera2_object = _setup_cameras_position(
        distance_from_object=distance_from_object,
        distance_between_cameras=distance_between_cameras,
        focal_length=focal_length,
    )

    _setup_light()

    # Set render resolution
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.context.scene.render.resolution_percentage = 100

    # Render images and save
    image_sides = ["right", "left"]
    for side, camera_object in zip(image_sides, [camera1_object, camera2_object]):
        bpy.context.scene.camera = camera_object
        bpy.context.scene.render.filepath = (output_dir / f"image_{side}.png").as_posix()
        bpy.ops.render.render(write_still=True)


def _setup_object(object_path: Path, object_scale: float):
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the STL file
    bpy.ops.import_mesh.stl(filepath=object_path.as_posix())

    # Center the object and adjust scale
    obj = bpy.context.selected_objects[0]  # Assuming only one object is imported
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    random_rotation = np.random.randint(0, 60, size=3)
    rotation = np.array([90, 0, 90]) + random_rotation
    obj.rotation_euler = np.deg2rad(rotation).tolist()
    obj.location = (0, 0, 0)
    obj.scale = (np.array([1, 1, 1]) * object_scale).tolist()

    # Apply a basic material to ensure the object is visible
    mat = bpy.data.materials.new(name="Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get("Principled BSDF")
    principled_bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)  # Light gray
    obj.data.materials.append(mat)


def _setup_cameras_position(distance_from_object: float, distance_between_cameras: float, focal_length: float):
    # Set up two cameras
    camera1_data = bpy.data.cameras.new(name="Camera1")
    camera1_data.lens = focal_length
    camera1_object = bpy.data.objects.new("Camera1", camera1_data)

    camera2_data = bpy.data.cameras.new(name="Camera2")
    camera2_data.lens = focal_length
    camera2_object = bpy.data.objects.new("Camera2", camera2_data)

    bpy.context.scene.collection.objects.link(camera1_object)
    bpy.context.scene.collection.objects.link(camera2_object)

    # Position the cameras
    distance_from_center = distance_between_cameras / 2
    camera1_object.location = (distance_from_object, distance_from_center, 0)
    camera2_object.location = (distance_from_object, -distance_from_center, 0)

    # Rotation the cameras
    camera_angle = np.rad2deg(np.arctan(distance_from_object / distance_from_center))
    camera1_object.rotation_euler = np.deg2rad([90, 0, 180 - camera_angle]).tolist()
    camera2_object.rotation_euler = np.deg2rad([90, 0, camera_angle]).tolist()

    return camera1_object, camera2_object


def _setup_light():
    # Set up a light source
    light_data = bpy.data.lights.new(name="Light_1", type="SUN")
    light_object = bpy.data.objects.new(name="Light_1", object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = (30, 0, 30)
    light_object.rotation_euler = (90, 0, 90)
    light_data.energy = 0.5  # Increase light intensity

    # Set up a light source
    light_data = bpy.data.lights.new(name="Light_2", type="SUN")
    light_object = bpy.data.objects.new(name="Light_2", object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = (0, 0, 50)
    light_object.rotation_euler = (0, 0, 90)
    light_data.energy = 2  # Increase light intensity

    # Ensure a world background exists and set its color
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    bpy.context.scene.world.color = (0.05, 0.05, 0.05)  # Dark gray


def blender_render(
    object_path: str,
    output_dir: str,
    object_scale: float,
    distance_between_cameras: float,
    distance_from_object: float,
    focal_length: float,
    resolution_x: int,
    resolution_y: int,
    num_pairs: int,
):
    np.random.seed(42)
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    for i in range(num_pairs):
        render_paired_images(
            object_path=Path(object_path),
            output_dir=Path(output_dir) / f"pair_{i}",
            object_scale=object_scale,
            distance_between_cameras=distance_between_cameras,
            distance_from_object=distance_from_object,
            focal_length=focal_length,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
        )


def main():
    parser = argparse.ArgumentParser(description="Render paired images using Blender.")
    parser.add_argument("--blender-path", type=str, required=True, help="Path to the Blender program.")
    parser.add_argument("--object-path", type=str, required=True, help="Path to the .stl file.")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save the rendered images.")
    parser.add_argument("--object-scale", type=float, default=5.0, help="Scale object in size.")
    parser.add_argument("--distance-between-cameras", type=float, default=412.0, help="Distance between the cameras.")
    parser.add_argument(
        "--distance-from-object",
        type=float,
        default=639.0,
        help="Distance from the center between the cameras to the object.",
    )
    parser.add_argument("--focal-length", type=float, default=80.0, help="Lens focal length in millimeters.")
    parser.add_argument("--resolution-x", type=int, default=5120, help="Width of the picture resolution.")
    parser.add_argument("--resolution-y", type=int, default=4096, help="Height of the picture resolution.")
    parser.add_argument("--num-pairs", type=int, default=10, help="Number of image pairs to render.")
    args = parser.parse_args()

    # Call Blender with the specified script and arguments
    blender_command = [
        args.blender_path,
        "--background",
        "--python",
        (Path(__file__).parent / "render.py").as_posix(),
        "--",
        args.object_path,
        args.output_dir,
        str(args.object_scale),
        str(args.distance_between_cameras),
        str(args.distance_from_object),
        str(args.focal_length),
        str(args.resolution_x),
        str(args.resolution_y),
        str(args.num_pairs),
    ]
    subprocess.run(blender_command, check=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :]

    blender_render(
        object_path=argv[0],
        output_dir=argv[1],
        object_scale=float(argv[2]),
        distance_between_cameras=float(argv[3]),
        distance_from_object=float(argv[4]),
        focal_length=float(argv[5]),
        resolution_x=int(argv[6]),
        resolution_y=int(argv[7]),
        num_pairs=int(argv[8]),
    )
