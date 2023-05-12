import asyncio
import random

from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.responses import StreamingResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

templates = Environment(
    loader=FileSystemLoader('templates'),
    enable_async=True
)


async def homepage(request):
    recommendations = [
        dict(name='Comfy Chair', discount_price=745.00, normal_price=800.00, review_count=1550, img='product1.jpg'),
        dict(name='Bed King Size', discount_price=1055.00, normal_price=1599.99, review_count=720, img='product4.jpg'),
        dict(name='Lounge pairs', discount_price=350.00, normal_price=499.99, review_count=952, img='product2.jpg'),
        dict(name='Air mattress', discount_price=189.99, normal_price=250.00, review_count=153, img='product3.jpg'),
    ]

    async def slow_recommendations():
        for r in recommendations:
            delay = random.randint(0, 500) / 100
            await asyncio.sleep(delay)
            yield r

    # return templates.TemplateResponse('index.html', {'request': request, 'recommendations': recommendations})
    template = templates.get_template('index.html')
    recommendations_t = templates.get_template('partials/_item.html')
    foo = recommendations_t.generate(items=recommendations)
    return StreamingResponse(
        content=template.generate_async(
            request=request,
            recommendations=slow_recommendations(),
            # foo=recommendations.generate_async(items=slow_recommendations())
            # foo=recommendations_t.generate_async(items=recommendations)
            foo=foo
        ),
        media_type='text/html',
    )


routes = [
    Route('/', endpoint=homepage),
    Mount('/static', StaticFiles(directory='static'), name='static')
]

app = Starlette(debug=True, routes=routes)
