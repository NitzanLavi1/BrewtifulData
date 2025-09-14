import os
import requests
from typing import Optional

class ImageManager:
    def __init__(self, image_url: str, image_dir: str) -> None:
        self.image_url = image_url
        self.image_dir = image_dir

    def has_image(self) -> bool:

        return bool(self.image_url)

    def image_filename(self) -> str:

        return self.image_url.split("/")[-1] if self.image_url else "N/A"

    def download_image(self) -> Optional[str]:
        if not self.has_image():

            return None
        image_name = self.image_filename()
        image_path = os.path.join(self.image_dir, image_name)
        img_resp = requests.get(self.image_url)
        with open(image_path, "wb") as f:
            f.write(img_resp.content)

        return image_path

    @staticmethod
    def remove_image(image_path: str) -> None:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)