import json

from aiohttp import web
from models import SessionDB, init_orm, engine, Post
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

app = web.Application()

async def create_orm_context(app):
    print('START')
    await init_orm()
    yield
    await engine.dispose()
    print('FINISH')

def generate_http_errors(error_class, msg: str | dict | list):
    return error_class(
        text=json.dumps(
            {'error': msg}
        ), 
        content_type='application/json',
        )

async def get_post_by_id(post_id: int, session: AsyncSession) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise generate_http_errors(web.HTTPNotFound, 'post is not found')
    return post

async def add_post(post: Post, session: AsyncSession) -> Post:
    session.add(post)
    try:
        await session.commit()
    except IntegrityError:
        raise generate_http_errors(web.HTTPConflict, 'post already exists')
    return post
    
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with SessionDB() as session:
        request.session = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(create_orm_context)
app.middlewares.append(session_middleware)

class PostView(web.View):

    @property
    def post_id(self) -> int:
        return int(self.request.match_info['post_id'])
    
    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get(self):
        post = await get_post_by_id(self.post_id, self.session)
        return web.json_response(post.dict)
    
    async def post(self):
        post_data = await self.request.json()
        post = Post(**post_data)
        post = await add_post(post, self.session)
        return web.json_response({'id': post.id})

    async def patch(self):
        post_data = await self.request.json()
        post = await get_post_by_id(self.post_id, self.session)
        for field, value in post_data.items():
            setattr(post, field, value)
        post = await add_post(post, self.session)
        return web.json_response({'id': post.id})

    async def delete(self):
        post = await get_post_by_id(self.post_id, self.session)
        await self.session.delete(post)
        await self.session.commit()
        return web.json_response({'status': f'post {self.post_id} is deleted'})
    
app.add_routes([
    web.get('/post/{post_id:\d+}/', PostView),
    web.delete('/post/{post_id:\d+}/', PostView),
    web.patch('/post/{post_id:\d+}/', PostView),
    web.post('/post/', PostView)
])

web.run_app(app)
