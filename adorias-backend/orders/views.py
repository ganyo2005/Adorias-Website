from urllib.parse import quote

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SpecialOrder, ProductEnquiry, WHATSAPP_NUMBER
from .serializers import SpecialOrderSerializer, ProductEnquirySerializer


def _wa_link(message):
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(message)}"


class SpecialOrderView(APIView):
    def post(self, request):
        serializer = SpecialOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            "order": SpecialOrderSerializer(order).data,
            "whatsapp_url": _wa_link(order.whatsapp_message()),
        }, status=201)


class ProductEnquiryView(APIView):
    def post(self, request):
        serializer = ProductEnquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save()
        return Response({
            "enquiry": ProductEnquirySerializer(enquiry).data,
            "whatsapp_url": _wa_link(enquiry.whatsapp_message()),
        }, status=201)
