from sanic import Sanic
from sanic import response

from sanic_session import InMemorySessionInterface
from sanic_jinja2 import SanicJinja2

import aiohttp

app = Sanic()

jinja = SanicJinja2(app)
session = InMemorySessionInterface(cookie_name=app.name, prefix=app.name)

head = """<!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
}
</style>
</head>
<body>
<table>
"""

footer = """</table>
</body>
</html>"""



@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session.save(request, response)

async def fetch(get_session, url):
    """
    Use session object to perform 'get' request on url
    """
    async with get_session.get(url) as result:
        return await result.json()


@app.route('/<user>/<repo>')
async def handle_request(request, user, repo):
        url = "https://api.github.com/repos/" + user + "/" + repo + ""
        
        async with aiohttp.ClientSession() as get_session:
               	result = await fetch(get_session, url)
                page = str(head)
                for key, value in result.items():
                        table = """<tr>
                                    <td>""" + str(key) + """</td>
                                    <td>""" + str(value) + """</td>
                                   </tr>"""
                        page += table
                page += footer


                return response.html(page)
                #return jinja.render('index.html', request, args=None)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=8000, workers=2)
