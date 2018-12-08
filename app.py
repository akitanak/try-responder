import responder
import time

api = responder.API()

@api.route('/status')
def status(req, resp):
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

if __name__ == '__main__':
    api.run(port=5000)