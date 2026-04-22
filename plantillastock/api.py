from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from .schemas import *
from core.utils.search_filter import search_filter

router = Router()
