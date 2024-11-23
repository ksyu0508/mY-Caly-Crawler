import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from easyocr import Reader

# Initialize the EasyOCR reader once at the start (reuse for efficiency)
reader = Reader(["en", "ko"], gpu=False)

async def fetch_image(image_url):
    """
    Asynchronously fetch an image from a URL.
    Args:
        image_url (str): The URL of the image.
    Returns:
        bytes: The image content as bytes.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch image from URL: {image_url}")
            return await response.read()

def sync_ocr(image_bytes):
    """
    Perform OCR synchronously using EasyOCR.
    Args:
        image_bytes (bytes): The image content as bytes.
    Returns:
        str: Extracted text from the image.
    """
    results = reader.readtext(image_bytes, detail=0)
    return ' '.join(results)

async def perform_ocr(image_url):
    """
    Perform OCR asynchronously using EasyOCR.
    Args:
        image_url (str): The URL of the image.
    Returns:
        str: Extracted text from the image.
    """
    try:
        # Fetch the image bytes asynchronously
        image_bytes = await fetch_image(image_url)
        
        # Use ThreadPoolExecutor to run the OCR synchronously in a separate thread
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            extracted_text = await loop.run_in_executor(pool, sync_ocr, image_bytes)
        
        return extracted_text
    except Exception as e:
        return f"An error occurred: {e}"

# async def main():
#     # URL of the image
#     image_url = "https://www.yonsei.ac.kr/_attach/editor_image/2024-10/mmtrqdtsdndv.png"

#     # Perform OCR
#     extracted_text = await perform_ocr(image_url)
#     print("Extracted Text:")
#     print(extracted_text)

# if __name__ == '__main__':
#     # Run the asynchronous main function
#     asyncio.run(main())
