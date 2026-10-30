from services.receipt import receipt_draft


def test_dropped_decimal_requires_corroboration():
    draft = receipt_draft('123 Main Street\nDate: 11/25/2025\nSubtotal $124.99\nTax $10.62\nTotal $13561\nThank you for shopping at 24 Hour\nFitness!')
    assert draft['amount_text'] == '135.61'
    assert draft['date'] == '2025-11-25'
    assert draft['description'] == '24 Hour Fitness'
    assert receipt_draft('Total $13561')['amount_text'] == ''


def test_never_fall_back_to_item_price_or_address():
    draft = receipt_draft('123 Main Street\nHeadphones $79.99\nCable $25.98')
    assert draft['amount_text'] == ''
    assert draft['description'] == 'Receipt purchase'


def test_conflicting_total_is_not_prefilled():
    assert receipt_draft('Subtotal $105.97\nTax $9.01\nTotal $110.98')['amount_text'] == ''


def test_split_label_and_shein_date():
    draft = receipt_draft('SHEIN\nDate: 11/24/2025\nSubtota I $105.97\nTax $9.01\nTota I $114.98')
    assert draft['amount_text'] == '114.98'
    assert draft['date'] == '2025-11-24'
    assert draft['description'] == 'SHEIN'


def test_cloud_decimal_commas_do_not_become_whole_dollars():
    assert receipt_draft('Subtotal $124,993\nTax $10,62\nTotal $135,61')['amount_text'] == '135.61'
    draft = receipt_draft('Subtota | $105,97\nTax $9,01\nTotal $114,98')
    assert draft['amount_text'] == '114.98'
    assert receipt_draft('Total $13,561')['amount_text'] == ''
    assert receipt_draft('Total $13,561.00')['amount_text'] == '13561.00'
