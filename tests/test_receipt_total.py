from services.capture import suggest


def test_split_ocr_total_label():
    text='USB-C Charging Cable $25.98\nSubtota I $105.97\nTax $9.01\nTota I $114.98'
    assert suggest(text,kind='Expense')['amount_text']=='114.98'


def test_payable_total_beats_item_price_and_subtotal():
    text='Headphones $79.99\nCable $25.98\nSubtotal $105.97\nTax $9.01\nTotal $114.98'
    assert suggest(text,kind='Expense')['amount_text']=='114.98'
