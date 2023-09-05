import asyncio
import random
import time

from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.responses import StreamingResponse, Response, HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

jinja_environment = Environment(
    loader=FileSystemLoader('templates'),
    enable_async=True
)

templates = Jinja2Templates('templates', env=jinja_environment)

recommendations = [
    dict(name='Comfy Chair', discount_price=745.00, normal_price=800.00, review_count=1550, img='product1.jpg'),
    dict(name='Bed King Size', discount_price=1055.00, normal_price=1599.99, review_count=720, img='product4.jpg'),
    dict(name='Lounge pairs', discount_price=350.00, normal_price=499.99, review_count=952, img='product2.jpg'),
    dict(name='Air mattress', discount_price=189.99, normal_price=250.00, review_count=153, img='product3.jpg'),
]


def sync_slow_recommendations():
    for r in recommendations:
        delay = random.randint(0, 500) / 100
        time.sleep(delay)
        yield r


async def slow_all_recommendations():
    out = []
    for r in recommendations:
        delay = random.randint(0, 500) / 100
        await asyncio.sleep(delay)
        out.append(r)
    for x in out:
        yield x


async def slow_recommendations():
    for r in recommendations:
        delay = random.randint(0, 500) / 100
        await asyncio.sleep(delay)
        yield r


def choose_view(request):
    return templates.TemplateResponse(request, 'loading_screen.html')


async def blocking(request):
    return templates.TemplateResponse(request, 'index.html', dict(recommendations=(list(sync_slow_recommendations()))))


async def stream_sections(request):
    # return templates.TemplateResponse('index.html', {'request': request, 'recommendations': recommendations})
    template = jinja_environment.get_template('index.html')
    return StreamingResponse(
        content=template.generate_async(
            request=request,
            recommendations=slow_all_recommendations(),
        ),
        media_type='text/html',
    )


async def stream_items(request):
    # return templates.TemplateResponse('index.html', {'request': request, 'recommendations': recommendations})
    template = jinja_environment.get_template('index.html')
    return StreamingResponse(
        content=template.generate_async(
            request=request,
            recommendations=slow_recommendations(),
        ),
        media_type='text/html',
    )

async def stream_skeletons(request):
    # return templates.TemplateResponse('index.html', {'request': request, 'recommendations': recommendations})
    template = jinja_environment.get_template('index.html')
    return StreamingResponse(
        content=template.generate_async(
            request=request,
            recommendations=slow_recommendations(),
            more_classes='skel'
        ),
        media_type='text/html',
    )



routes = [
    Route('/', endpoint=choose_view),
    Route('/block', endpoint=blocking),
    Route('/stream-sections', endpoint=stream_sections),
    Route('/stream-items', endpoint=stream_items),
    Route('/skel', endpoint=stream_skeletons),
    Mount('/static', StaticFiles(directory='static'), name='static')
]

app = Starlette(debug=True, routes=routes)
