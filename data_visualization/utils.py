import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer,  format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_chart(mydict, chart_type, title):
    
    mydict = dict(sorted(mydict.items()))
    x = list(mydict.keys())
    y = list(mydict.values())

    # for key,val in mydict.items():
    #     x.append(key)
    #     y.append(val)
    title = "Title: " + title
    title = title.replace("_", " ")

    plt.switch_backend('AGG')
    plt.figure(figsize=(10,7))
    plt.title(title)

    if chart_type=='pie':
        plt.pie(y, labels=x, autopct='%0.1f%%', radius=1)
    elif chart_type=='donut':
        plt.pie(y, labels=x, autopct='%0.1f%%', radius=1)
        plt.pie([1],colors=['w'], radius=0.5)
    elif chart_type=='plot':
        # x = [1,2,3,4,5,6,7,8,9]
        # y = [5,2,6,8,1,3,4,1,7]
        print()
        print("X: ", x)
        print("Y: ", x)
        print()
        plt.plot(x,y)
        plt.scatter(x,y)
        plt.xlabel("Height")
        plt.xticks(x, x)
        plt.ylabel("Weight")
        plt.yticks(y, y)
    else:
        plt.bar(x,y)
        # plt.grid(True)

    plt.tight_layout()
    graph = get_graph()
    return graph
