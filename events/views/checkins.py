from .base import *


# Create your views here.
class TestingQRCodeView(HouseAccountMixin, View):
    template_name = "events/qr_code.html"

    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        data = request.POST
        print("It came to post")
        print(data)
        
        return HttpResponse("Checked IN!")
