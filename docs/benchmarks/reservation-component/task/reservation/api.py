"""In-process request adapter; no transport or authentication."""


def handle(service, request):
    return service.submit(request['tenant'], request['lines'])
