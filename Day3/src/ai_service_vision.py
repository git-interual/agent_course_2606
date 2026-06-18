# image 분석
# pip install azure-ai-vision-imageanalysis
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

def sample_analyze_all_image_file():
    endpoint = os.getenv("AZURE_AI_ENDPOINT")
    api_key = os.getenv("AZURE_AI_API_KEY")

    client = ImageAnalysisClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(api_key),
        logging_enable=True,
    )

    # load *.jpg file names from '.'
    files = [f for f in os.listdir('.') if f.endswith('.jpg')]

    for image_path in files:
        print("-" * 60)
        print(f"Opening {image_path}...")
        with open(image_path, "rb") as f:
            image_data = f.read()
            print(f"Analyzing {image_path}...")

            result = client.analyze(
                image_data=image_data,
                visual_features=[
                    VisualFeatures.TAGS,
                    VisualFeatures.OBJECTS,
                    # VisualFeatures.CAPTION,
                    # VisualFeatures.DENSE_CAPTIONS,
                    VisualFeatures.READ,
                    VisualFeatures.SMART_CROPS,
                    VisualFeatures.PEOPLE,
                ],  # Mandatory. Select one or more visual features to analyze.
                smart_crops_aspect_ratios=[0.9, 1.33],  # Optional. Relevant only if SMART_CROPS was specified above.
                gender_neutral_caption=True,  # Optional. Relevant only if CAPTION or DENSE_CAPTIONS were specified above.
                language="en",  # Optional. Relevant only if TAGS is specified above. See https://aka.ms/cv-languages for supported languages.
                model_version="latest",  # Optional. Analysis model version to use. Defaults to "latest".
            )

            # Print all analysis results to the console
            print("Image analysis results:")

            if result.caption is not None:
                print(" Caption:")
                print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

            if result.dense_captions is not None:
                print(" Dense Captions:")
                for caption in result.dense_captions.list:
                    print(f"   '{caption.text}', {caption.bounding_box}, Confidence: {caption.confidence:.4f}")
            print(result)



    # features = [VisualFeatures.DESCRIPTION, VisualFeatures.OBJECTS, VisualFeatures.CATEGORIES]
    # result = client.analyze_image(image=image_data, visual_features=features)

    # print("Description:", result.description.captions[0].text)
    # print("Objects:")
    # for obj in result.objects:
    #     print(f" - {obj.object_property} at {obj.rectangle}")
    
    # # 이미지에 객체 표시
    # img = Image.open(image_path)
    # draw = ImageDraw.Draw(img)
    # for obj in result.objects:
    #     rect = obj.rectangle
    #     draw.rectangle([(rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h)], outline="red", width=2)
    #     draw.text((rect.x, rect.y - 10), obj.object_property, fill="red")
    
    # img.show()

if __name__ == "__main__":
    sample_analyze_all_image_file()
