from google.cloud import vision_v1 as vision
from google.cloud import storage
import json, re

GCS_INPUT_URI  = "gs://urdu-pdf-bucket/input/urd_HR1.pdf"          # 确保已上传
GCS_OUTPUT_URI = "gs://urdu-pdf-bucket/output/urdu_ocr_results1/"  # 以 / 结尾

def run_async_pdf_ocr():
    client = vision.ImageAnnotatorClient()
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    gcs_source = vision.GcsSource(uri=GCS_INPUT_URI)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf")
    gcs_destination = vision.GcsDestination(uri=GCS_OUTPUT_URI)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=5)
    image_context = vision.ImageContext(language_hints=['ur'])

    request = vision.AsyncAnnotateFileRequest(
        features=[feature],
        input_config=input_config,
        output_config=output_config,
        image_context=image_context
    )
    op = client.async_batch_annotate_files(requests=[request])
    print("Processing... this may take a while.")
    op.result(timeout=1800)
    print("Done. Results saved to GCS.")

def download_and_merge_text():
    storage_client = storage.Client()
    bucket_name = re.match(r"gs://([^/]+)/", GCS_OUTPUT_URI).group(1)
    prefix = re.sub(r"^gs://[^/]+/", "", GCS_OUTPUT_URI)  # e.g. output/urdu_ocr_results/

    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))  # ✅ 正确用法

    pages_text = []
    for b in sorted(blobs, key=lambda x: x.name):
        if not b.name.endswith(".json"):
            continue
        data = json.loads(b.download_as_text(encoding="utf-8"))
        for resp in data.get("responses", []):
            full = resp.get("fullTextAnnotation", {})
            pages_text.append(full.get("text", ""))

    merged = re.sub(r"\n{3,}", "\n\n", "\n".join(pages_text)).strip()
    with open("urdu_ocr_output.txt", "w", encoding="utf-8") as f:
        f.write(merged)
    print("Saved -> urdu_ocr_output.txt")

if __name__ == "__main__":
    run_async_pdf_ocr()
    download_and_merge_text()
