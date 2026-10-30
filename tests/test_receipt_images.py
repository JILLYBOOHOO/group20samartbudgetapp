"""Exercise the actual Cloud Poppler/Tesseract pipeline on supplied fake receipts."""
import shutil
from pathlib import Path
import pytest
from services.ocr import photo_to_pdf, portable_ocr_pdf
from services.receipt import receipt_draft


@pytest.mark.skipif(not (shutil.which('tesseract') and shutil.which('pdftoppm')), reason='Linux OCR tools required')
@pytest.mark.parametrize('filename,amount,day,merchant', [
    ('fitness.png', '135.61', '2025-11-25', '24 Hour Fitness'),
    ('shein.png', '114.98', '2025-11-24', 'SHEIN'),
])
def test_cloud_receipt_image(filename, amount, day, merchant, tmp_path):
    image = Path(__file__).with_name('fixtures') / filename
    text = portable_ocr_pdf(photo_to_pdf(image.read_bytes()), tmp_path)
    draft = receipt_draft(text)
    print('\nOCR:', filename, '\n', text, '\nDraft:', draft)
    assert draft['amount_text'] == amount
    assert draft['date'] == day
    assert draft['description'] == merchant
