import json
import os
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from pydantic import ValidationError
# from .json_converter import JsonConverter
from .data_loader import JsonLoader, XmlLoader, ImageLoader
from .xml_parser import XMLParser


def handle_exchange_test(request):
    parser = XMLParser(xml_file=request.GET.get('path'))
    parser.parse_file()
    with transaction.atomic():
        XmlLoader(parser)
    return HttpResponse('Тест окончен')



@csrf_exempt
def exchange(request):

    if request.method == 'GET':
        if request.GET.get('type') == 'catalog' and request.GET.get('mode') == 'checkauth':
            # cookname - имя секретной куки, cookvalue - значение секретной куки
            return HttpResponse('success\ncookname\ncookvalue')

        if request.GET.get('type') == 'catalog' and request.GET.get('mode') == 'init':
            return HttpResponse('zip=no\nfile_limit=35000000')

        return HttpResponse('success')

    if request.method == 'POST':
        # 'type=catalog&mode=file&filename=import0_1_BIG.xml'
        # 'type=catalog&mode=file&filename=import_files/48/48d21364ad3411e5acd4000d884fd00d_48d21365ad3411e5acd4000d884fd00d.jpg'
        # First part is PRODUCT_ID 48d21364-ad34-11e5-acd4-000d884fd00d
        type = request.GET.get('type')
        mode = request.GET.get('mode')
        filename = request.GET.get('filename')

        if type == 'catalog' and mode == 'file' and filename:

            input_filepath = Path(filename)
            if _is_it_xml(input_filepath):
                _load_xml(request, input_filepath)
            else:
                loader = ImageLoader(request, input_filepath)
                loader.save_image()

        return HttpResponse('success')


def _is_it_xml(path):

    if len(path.parts) == 1 and path.suffix == '.xml':
        return True
    return False


def _load_xml(request, input_filepath):

    absolute_path = settings.BASE_DIR / input_filepath.name
    absolute_path.write_bytes(request.body)
    parser = XMLParser(xml_file=absolute_path)
    parser.parse_file()

    with transaction.atomic():
        XmlLoader(parser)


def _load_json(request):
    # НА ДОРАБОТКЕ
    pass
    # if request.method == 'POST':
    #     try:
    #         body = json.loads(request.body)
    #         input_data = JsonConverter(body)
    #         data_loader = DataLoader(input_data)
    #     except JSONDecodeError as e:
    #         response = "JSON DECODE ERROR\n\n" + traceback.format_exc()
    #     except ValidationError as e:
    #         response = traceback.format_exc()
    #     except Exception as e:
    #         response = "Error\n\n" + traceback.format_exc()
    #     else:
    #         response = 'load_json'
    #     finally:
    #         del input_data
    #         return HttpResponse(response)
