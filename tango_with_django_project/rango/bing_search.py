import webhoseio

def config():
    webhoseio.config(token='5b1cf08e-1b7b-4b5e-ba7f-8210940a6cbd')

def run_query(query):
    config()
    print("Hello")
    final_output = []
    output = webhoseio.query("filterWebContent", {"q":query})
    for post in output['posts']:
        final_output.append({'title': post['title'], 'text': post['text'][0:200], 'url': post['url']})
    return final_output

