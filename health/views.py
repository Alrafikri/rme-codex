from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def healthz(_request):
    return Response({"ok": True})
