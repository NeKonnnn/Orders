from PIL import Image

import constants


def convert_to_favicon(source_image_path: str, ico_output_path: str) -> None:
    try:
        # Open the image using Pillow
        img = Image.open(source_image_path)

        # Ensure the image is in the correct size (32x32 pixels)
        img = img.resize((64, 64))

        # Save the image as an ICO file
        img.save(ico_output_path, format="ICO")

        print(f"Image converted to favicon.ico and saved to {ico_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    image_path = "../images/icon.png"
    output_path = "../" + constants.ICON_PATH

    convert_to_favicon(image_path, output_path)
