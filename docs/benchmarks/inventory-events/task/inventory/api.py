def handle(ledger, request):
    return ledger.apply(request['events'])
