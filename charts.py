import pandas as pd
import circlify
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import os

def make_bubble_graph(data):

    if os.path.isfile("static/images/bubble_graph_200.jpg"):
        os.remove("static/images/bubble_graph_200.jpg")
    sorted_data = {}
    sorted_keys = sorted(data, key=data.get)[-5:]

    for w in sorted_keys:
        sorted_data[w] = data[w]
    
    for value in sorted_data.values():
        value = value if value > 0 else 0.1

    circles = circlify.circlify(
    sorted_data.values(), 
    show_enclosure=False, 
    target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )  

    fig, ax = plt.subplots(figsize=(5,5))
    ax.axis('off')
    ax.set_title('Top 5 topics distribution')
    labels = sorted_data.keys()
    colors = ['#FF5733', '#C70039', '#900C3F', '#581845', '#2C3E50', '#7D6608', '#7E5109', '#784212', '#512E5F', '#283747', '#154360', '#0E6251', '#145A32', '#1B4F72', '#7E5109', '#784212', '#2E4053', '#2C2C54', '#8E44AD']

    lim = max(
    max(
        abs(circle.x) + circle.r,
        abs(circle.y) + circle.r,
    )
    for circle in circles
    )   

    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    for circle, label, color in zip(circles, labels, colors):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.8, linewidth=2, color=color))
        plt.annotate(
            label, 
            (x,y ) ,
            va='center',
            ha='center'
        )
    print(data.values())
    print(data.keys())

    plt.savefig("static/images/bubble_graph_200.jpg", facecolor='#0d1422',dpi=200)
    img = Image.open("static/images/bubble_graph_200.jpg")
    data = io.BytesIO()
    img.save(data,"JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data