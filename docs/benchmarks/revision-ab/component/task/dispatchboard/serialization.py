"""Stable boundary conversion for receipts."""


def receipt_to_dict(receipt):
    return {
        "event_id": receipt.event_id,
        "accepted": receipt.accepted,
        "details": dict(receipt.details),
    }
