import json

from django.views import View
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404

from ..models import Category, Product, ProductImage


class CategoryListView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        categories = [
            {
                "id": cat.pk,
                "name": cat.name,
                "description": cat.description,
                "created_at": cat.created_at.isoformat(),
                "updated_at": cat.updated_at.isoformat()
            }
            for cat in Category.objects.all()
        ]

        return JsonResponse({'categories': categories})

    def post(self, request: HttpRequest) -> JsonResponse:
        data = json.loads(request.body)

        name = data.get('name')
        if not name:
            return JsonResponse({'name': 'Required.'}, status=400)
        elif len(name) > 128:
            return JsonResponse({'name': 'Max 128 characters.'}, status=400)
        
        try:
            Category.objects.get(name=name)
            return JsonResponse({'name': 'Unique.'}, status=400)
        except Category.DoesNotExist:
            category = Category(
                name=data['name'],
                description=data.get('description')
            )
            category.save()

            return JsonResponse(
                {
                    "id": category.pk,
                    "name": category.name,
                    "description": category.description,
                    "created_at": category.created_at.isoformat(),
                    "updated_at": category.updated_at.isoformat()
                },
                status=201
            )


class CategoryDetailView(View):
    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        category = get_object_or_404(Category, pk=pk)

        # try:
        #     category = Category.objects.get(pk=pk)
        # except Category.DoesNotExist:
        #     return JsonResponse({'category': 'not found.'}, status=404)
        
        return JsonResponse({
                "id": category.pk,
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat()
            })

    def put(self, request: HttpRequest, pk: int) -> JsonResponse:
        category = get_object_or_404(Category, pk=pk)

        data = json.loads(request.body)

        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)

        category.save()

        return JsonResponse(
            {
                "id": category.pk,
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat()
            },
            status=204
        )

    def delete(self, request: HttpRequest, pk: int) -> JsonResponse:
        category = get_object_or_404(Category, pk=pk)

        category.delete()

        return JsonResponse({'category': 'Deleted.'}, status=204)
