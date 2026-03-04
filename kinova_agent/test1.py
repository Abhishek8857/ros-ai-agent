import os
import io
import json
import base64
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -----------------------
# 1. Load API Key
# -----------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("API key not found! Put it in .env as GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# -----------------------
# Helper: parse JSON from markdown fencing
# -----------------------
def parse_json(json_output: str):
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "```json":
            json_output = "\n".join(lines[i + 1 :])
            output = json_output.split("```")[0]
            return output
    return json_output

# -----------------------
# Helper: load RGB array from .npy or .npz
# -----------------------
def load_rgb_array(path: str) -> np.ndarray:
    """
    Loads an RGB image array from either:
    - .npy  (saved array)
    - .npz  (dict-like container with one or more arrays)

    Returns a NumPy array of shape (H, W, 3).
    """
    data = np.load(path)

    # If it's an npz (NpzFile), select a suitable key
    if isinstance(data, np.lib.npyio.NpzFile):
        print(f"Loaded NPZ file: {path}")
        print("Available keys:", data.files)

        preferred_keys = ["rgb", "color", "image", "rgb_image", "color_image"]
        key_to_use = None

        # Try preferred keys first
        for k in preferred_keys:
            if k in data.files:
                key_to_use = k
                break

        # If no preferred key, just take the first one
        if key_to_use is None:
            key_to_use = data.files[0]
            print(f"No preferred key found, using first key: {key_to_use}")
        else:
            print(f"Using key: {key_to_use}")

        arr = data[key_to_use]
    else:
        # .npy case: data is already a NumPy array
        arr = data

    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(
            f"Loaded array has shape {arr.shape}, which doesn't look like (H, W, 3+)."
        )

    # If more than 3 channels, keep only RGB
    if arr.shape[2] > 3:
        arr = arr[:, :, :3]

    # Ensure uint8
    arr = arr.astype(np.uint8)
    return arr

# -----------------------
# Main function to extract segmentation masks
# -----------------------
def extract_segmentation_masks_from_npy(
    rgb_npy_path: str,
    objects: list,
    output_dir: str = "/home/ubuntu/workspaces/kinova_ws/src/kinova-transfer/hack_fld",
):
    # -----------------------
    # 0. Load original NPZ to get depth and K (if available)
    # -----------------------
    depth = None
    K = None

    data = np.load(rgb_npy_path)
    if isinstance(data, np.lib.npyio.NpzFile):
        if "depth" in data.files:
            depth = data["depth"]
        if "K" in data.files:
            K = data["K"]
        print("Depth present:", depth is not None)
        print("K present:", K is not None)
    else:
        print("Warning: input is not .npz, depth and K will not be saved in the output.")

    # -----------------------
    # 1. Load RGB from .npy/.npz and convert to Pillow Image
    # -----------------------
    rgb_array = load_rgb_array(rgb_npy_path)  # shape: (H, W, 3)
    full_res_im = Image.fromarray(rgb_array)  # full resolution image
    original_size = full_res_im.size  # (W, H)
    orig_w, orig_h = original_size

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create resized copy for Gemini (max 1024x1024)
    im = full_res_im.copy()
    # Use Image.LANCZOS for compatibility with older Pillow
    im.thumbnail([1280, 720], Image.LANCZOS)

    # Convert resized image to PNG bytes for Gemini
    with io.BytesIO() as buf:
        im.save(buf, format="PNG")
        image_bytes = buf.getvalue()

    # Prepare prompt
    obj_list = ", ".join(objects)
    prompt = f"""
    You are a robotics vision model.
    Segment ONLY the following objects: {obj_list}, but only their RED parts.

    Output a JSON list of segmentation masks where each entry contains:
    - "box_2d": 2D bounding box [ymin, xmin, ymax, xmax] normalized 0-1000
    - "mask": PNG mask in base64
    - "label": text label for the object

    Rules:
    - Keep original size, do not resize or crop masks
    - Background = pure black (0,0,0)
    - Only the RED portion of the object should be visible in the mask
    """

    # -----------------------
    # Call Gemini ER 1.5
    # -----------------------
    response = client.models.generate_content(
        model="gemini-robotics-er-1.5-preview",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )

    # Parse JSON
    items = json.loads(parse_json(response.text))

    # -----------------------
    # Prepare a single segmap (union of all masks)
    # -----------------------
    resized_w, resized_h = im.size

    # scale from resized → original
    scale_x = orig_w / resized_w
    scale_y = orig_h / resized_h

    segmap = Image.new("L", (orig_w, orig_h), 0)  # full-size segmentation map
    seg_pixels = segmap.load()

    for i, item in enumerate(items):
        box = item["box_2d"]
        # box is [ymin, xmin, ymax, xmax] in [0, 1000]
        y0 = int(box[0] / 1000 * resized_h)
        x0 = int(box[1] / 1000 * resized_w)
        y1 = int(box[2] / 1000 * resized_h)
        x1 = int(box[3] / 1000 * resized_w)

        if y0 >= y1 or x0 >= x1:
            print(f"Skipping invalid box: {box}")
            continue

        # Decode mask and create local mask
        png_str = item["mask"]
        if png_str.startswith("data:image/png;base64,"):
            png_str = png_str.removeprefix("data:image/png;base64,")
        mask_data = base64.b64decode(png_str)
        mask = Image.open(io.BytesIO(mask_data)).convert("L")
        # Use Image.BILINEAR for compatibility
        mask = mask.resize((x1 - x0, y1 - y0), Image.BILINEAR)
        mask_array = np.array(mask)

        # Map resized mask box to original coordinates, update segmap
        for y in range(y0, y1):
            for x in range(x0, x1):
                orig_x = int(x * scale_x)
                orig_y = int(y * scale_y)
                if 0 <= orig_x < orig_w and 0 <= orig_y < orig_h:
                    if mask_array[y - y0, x - x0] > 128:
                        seg_pixels[orig_x, orig_y] = 255

    # -----------------------
    # Save final segmap.png
    # -----------------------
    segmap_png_path = os.path.join(output_dir, "segmap.png")
    segmap.save(segmap_png_path)
    print(f"Saved segmap PNG to {segmap_png_path}")

    # Convert segmap to numpy
    segmap_array = np.array(segmap)

    # -----------------------
    # Save combined segmap + rgb + depth + K into one .npz
    # -----------------------
    combined_npz_path = os.path.join(output_dir, "segmap_rgb_depth_K.npz")

    # Build kwargs dynamically based on what we have
    npz_kwargs = {
        "segmap": segmap_array,
        "rgb": rgb_array,   # original RGB image as numpy array
    }
    if depth is not None:
        npz_kwargs["depth"] = depth
    if K is not None:
        npz_kwargs["K"] = K

    np.savez(combined_npz_path, **npz_kwargs)
    print(f"Saved combined segmap/rgb/depth/K to {combined_npz_path}")

    # -----------------------
    # Print resolution check
    # -----------------------
    print(f"RGB input resolution: {rgb_array.shape[1]}x{rgb_array.shape[0]}")
    print(f"Segmap resolution: {segmap_array.shape[1]}x{segmap_array.shape[0]}")
    if (
        rgb_array.shape[0] == segmap_array.shape[0]
        and rgb_array.shape[1] == segmap_array.shape[1]
    ):
        print("Resolution match ✅")
    else:
        print("Resolution mismatch ❌")


# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    rgb_npy_file = (
        "/home/ubuntu/workspaces/kinova_ws/src/kinova-transfer/rgbd_image.npz"
    )  # <-- Input RGB .npz with keys: rgb, depth, K
    objects_to_segment = ["Tape", "Bottle", "Box"]  # Objects to segment
    extract_segmentation_masks_from_npy(rgb_npy_file, objects_to_segment)
