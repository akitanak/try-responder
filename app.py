from datetime import datetime

import responder
import time

api = responder.API()

@api.route('/status')
def status(req, resp):
    resp.status_code = api.status_codes.HTTP_200
    resp.text = "I'm fine. Thank you."

# パスから引数を受け取る
@api.route('/hello/{name}')
def hello_to(req, resp, *, name):
    resp.text=f'Hello, {name}!'

# JSON/YAMLを返す
# accept ヘッダーの値(application/json, application/x-yaml)に従ったフォーマットで返す
@api.route('/medias/{format}')
def get_media(req, resp, *, format):
    resp.media = { 
        "media_format": format,
        "list": [1, 2, 3, 4]
    }

# ステータスコードを設定する
@api.route('/are/you/tea_pot')
def are_you_tea_pot(req, resp):
    resp.status_code = 418
    resp.text = "I'm a tea pot."

# テンプレートをレンダリングする
@api.route('/hello/{name}/html')
def hello_html(req, resp, *, name):
    resp.content = api.template('hello.html', name=name)

# レスポンスヘッダを設定する
@api.route('/Hi')
def hi_how_are_you(req, resp):
    resp.headers['X-reply'] = 'How are you?'

# 送信されたデータを受信する(json)
@api.route('/give/me/some/data')
async def give_me_some_data(req, resp):
    # req.mediaの引数にformatが指定できる(json/yaml/form)
    # 未指定の場合は、リクエストヘッダのcontent-typeに従って読み込まれる。
    data = await req.media()
    print(data)

    resp.media = { 'reply': 'Thank you.' }

# リクエストを受けたスレッドとは別のスレッドでバックグラウンド処理を行う
@api.route('/background/task')
async def background_task(req, resp):

    @api.background.task
    def process_data(data):
        time.sleep(5) 
        print(data)

    data = await req.media()
    print('dispatch background process')
    process_data(data)
    print('return greeting')
    resp.text = 'received.'

# Classでルートを定義する。
@api.route('/images')
class Images:
    def on_get(self, req, resp):
        resp.media = [
            { 'id': 1, 'name': 'image1.png' },
            { 'id': 2, 'name': 'image2.png' }
        ]
    
    async def on_post(self, req, resp):
        data = await req.media()
        print(data)
        resp.media = data
        resp.status_code = 201

@api.route('/images/{id}')
class Image:
    def on_get(self, req, resp, *, id):
        resp.media = { 'id': id, 'name': f'image{id}.png'}
    
    async def on_put(self, req, resp, *, id):
        data = await req.media()
        resp.media = data
        resp.status_code = 200

# GraphQL
import graphene

class Query(graphene.ObjectType):
    task = graphene.String(taskName=graphene.String(default_value="empty"))

    def resolve_task(self, info, taskName):
        print(info)
        return f'task: {taskName}'

schema = graphene.Schema(query=Query)
view = responder.ext.GraphQLView(api=api, schema=schema)

api.add_route('/graph', view)

@api.on_event('startup')
async def startup():
    print('start up my server.')

@api.on_event('shutdown')
async def shutdown():
    print('shutdown my server.')


# NOTE: Responder のドキュメントを見ると、on_event の event_type として cleanup, tick も記述されているが、
#       実装を見ると実際の処理は add_event_handler に委譲されており、今の所 startup と shutdown にのみ対応しているようだ。

# @api.on_event('cleanup')
# async def cleanup():
#     print('cleanup')

# @api.on_event('tick', seconds=10)
# async def tick():
#     print(datetime.now())

# api.add_event_handler('startup', startup)
# api.add_event_handler('shutdown', shutdown)

if __name__ == '__main__':
    api.run(port=5000)
