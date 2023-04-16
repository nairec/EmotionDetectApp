# Import necessary libraries
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification,pipeline
from flask import Flask,render_template,request,jsonify
import snscrape.modules.twitter as snstwitter
from statistics import mode
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from jinja2 import Environment, PackageLoader
from dotenv import load_dotenv
import json
import os
import mpld3

from topic_detect import get_topics
from charts import make_bubble_graph, make_doughnut_chart

load_dotenv()
app = Flask(__name__)
env = Environment(loader=PackageLoader(__name__, 'templates'))
env.filters['json'] = json.dumps
tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")
emotion_task_top_result = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
emotion_task_all_results = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa', top_k=None)
sentiment_task = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment", tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment")
youtube = build('youtube', 'v3', developerKey=os.environ.get("YOUTUBE_API_KEY"))
file_uploads = os.path.abspath("static/files")

@app.route('/home',methods=["POST","GET"])
def home():
    return render_template('home.html')

@app.route('/features',methods=["POST","GET"])
def features():
    return render_template('features.html')

@app.route('/text-scanner',methods=["POST","GET"])
def text_scanner():
    if request.method == "POST":
        input = request.form["nm"]
        mode = request.form["mode"]
        sentiment = classify_text_sentiment(input,mode)
        emotion = classify_text_emotion(input,mode)
        topics = get_topics(input)
        bubble_graph = make_bubble_graph(topics)
        return render_template('text-scanner.html',sentiment=sentiment,emotion=emotion,input=input,bubble_graph=bubble_graph)
    else:
        sentiment = "Input sentiment"
        emotion = "Input emotion"
        input=""
        return render_template('text-scanner.html',sentiment=sentiment,emotion=emotion,input=input)

@app.route('/twitter-scanner',methods=["POST","GET"])
def twitter_scanner():
    if request.method == "POST":
        user = request.form["user"]
        since = request.form["since"]
        until = request.form["until"]
        query = f"(from:{user}) until:{until} since:{since}"
        positive_result,neutral_result,negative_result = analyze_twitter(query)
    else:
        positive_result,neutral_result,negative_result = ["","",""]
    return render_template('twitter-scanner.html',positive_result=positive_result,neutral_result=neutral_result,negative_result=negative_result)

@app.route('/youtube-scanner',methods=["POST","GET"])
def youtube_scanner():
    if request.method == "POST":
        video_link = request.form["link"]
        max_results = request.form["max_results"]
        video_link = video_link[-11:]
        positive_result,neutral_result,negative_result,total_emotions,topics = analyse_youtube(video_link,int(max_results))
        bubble_graph_topics = make_bubble_graph(topics)
        print(f"emotions: {total_emotions}")
        bubble_graph_emotions = make_bubble_graph(total_emotions)
        return env.get_template('youtube-scanner.html').render(positive_result=positive_result,neutral_result=neutral_result,negative_result=negative_result,total_emotions=total_emotions,topics=topics,bubble_graph_topics=bubble_graph_topics.decode('utf-8'),bubble_graph_emotions=bubble_graph_emotions.decode('utf-8'))
    else:
        positive_result,neutral_result,negative_result = ["","",""]
        total_emotions = {'love':0,'admiration':0,'joy':0,'approval':0,'caring':0,'excitement':0,'amusement':0,'gratitude':0,'desire':0,'anger':0,'optimism':0,'disapproval':0,'grief':0,'annoyance':0,'pride':0,'curiosity':0,'neutral':0,'disgust':0,'disappointment':0,'realization':0,'fear':0,'relief':0,'confusion':0,'remorse':0,'embarrassment':0,'surprise':0,'sadness':0,'nervousness':0}
        topics = {"arts_&_culture":0,"fashion_&_style":0,"learning_&_educational":0,"science_&_technology":0,"business_&_entrepreneurs":0,"film_tv_&_video":0,"music":0,"sports":0,"celebrity_&_pop_culture":0,"fitness_&_health":0,"news_&_social_concern":0,"travel_&_adventure":0,"diaries_&_daily_life":0,"food_&_dining":0,"other_hobbies":0,"youth_&_student_life":0,"family":0,"gaming":0,"relationships":0}
        return env.get_template('youtube-scanner.html').render(positive_result=positive_result,neutral_result=neutral_result,negative_result=negative_result,total_emotions=total_emotions,topics=topics)

@app.route('/file-scanner',methods=["POST","GET"])
def file_scanner():
    if request.method == "POST":
        file = request.files["file"]
        mode = request.form["mode"]
        file.save(os.path.join(file_uploads,file.filename))
        sentiment,emotion,topics = file_scan(mode,file)
        bubble_graphic_topics = make_bubble_graph(topics)
        bubble_graphic_emotions = make_bubble_graph(emotion)
        doughnut_graphic_topics = make_doughnut_chart(topics)
        dominant_emotion_label = max(emotion, key=emotion.get)
        dominant_emotion = f" dominant emotion: {dominant_emotion_label}, score: {emotion[dominant_emotion_label]}%"
        return env.get_template('file-scanner.html').render(sentiment=sentiment,emotion=emotion,dominant_emotion=dominant_emotion,topics=topics,bubble_graph_topics=bubble_graphic_topics,bubble_graph_emotions=bubble_graphic_emotions,doughnut_graph_topics=doughnut_graphic_topics)
    else:
        sentiment = "File sentiment"
        dominant_emotion = "Dominant file emotion"
        emotion = {'love':0,'admiration':0,'joy':0,'approval':0,'caring':0,'excitement':0,'amusement':0,'gratitude':0,'desire':0,'anger':0,'optimism':0,'disapproval':0,'grief':0,'annoyance':0,'pride':0,'curiosity':0,'neutral':0,'disgust':0,'disappointment':0,'realization':0,'fear':0,'relief':0,'confusion':0,'remorse':0,'embarrassment':0,'surprise':0,'sadness':0,'nervousness':0}
        topics = {"arts_&_culture":0,"fashion_&_style":0,"learning_&_educational":0,"science_&_technology":0,"business_&_entrepreneurs":0,"film_tv_&_video":0,"music":0,"sports":0,"celebrity_&_pop_culture":0,"fitness_&_health":0,"news_&_social_concern":0,"travel_&_adventure":0,"diaries_&_daily_life":0,"food_&_dining":0,"other_hobbies":0,"youth_&_student_life":0,"family":0,"gaming":0,"relationships":0}
    return env.get_template('file-scanner.html').render(sentiment=sentiment,emotion=emotion,dominant_emotion=dominant_emotion,topics=topics)

#Define algorithm for poem classification
def sentiment_algorithm(sentiment_list):
    total_value = 0
    positive = 0
    negative = 0
    non_neutral_verses = sum(1 for verse in sentiment_list if verse['label'] == "positive" or verse['label'] == "negative")
    
    for sentiment in sentiment_list:
        if sentiment["label"] == "neutral":
            pass
        elif sentiment["label"] == "positive":
            positive += sentiment["score"]
        elif sentiment["label"] == "negative":
            negative += sentiment["score"] 
    total_value = round((positive-negative)/non_neutral_verses,2)*100 if non_neutral_verses > 0 else total_value

    if total_value < 0:
        result = "negative"
        sentiment = "negatividad"
        return f"sentiment del poema: {result}, índice de {sentiment}: {abs(total_value)}%"
    elif total_value > 0:
        result = "positive"
        sentiment = "positividad"
        return f"sentiment del poema: {result}, índice de {sentiment}: {abs(total_value)}%"
    else:
        result= "neutral"
        return f"sentiment del poema: {result}"


# Define classification function
def classify_text_sentiment(text,mode):
    if mode == "phrase":
        sentiment_result = sentiment_task(text)[0]

        if sentiment_result['label'] == 'positive':
            result = "positive"
            sentiment = "positividad"
            return f"poem sentiment: {result}, índice de {sentiment}: {round(sentiment_result['score']*100,2)}%"
        elif sentiment_result['label'] == 'negative':
            result = "negative"
            sentiment = "negatividad"
            return f"sentiment del poema: {result}, índice de {sentiment}: {round(sentiment_result['score']*100,2)}%"
        else:
            return f"sentiment del poema: neutral"
        
    elif mode == "text":
        pass
    elif mode == "poem":
        sentiment_list = []
        text = text.split(";")
        for verse in text:
            result = sentiment_task(verse)
            sentiment_list.append(result[0])
        return sentiment_algorithm(sentiment_list)
    
def classify_text_emotion(text,mode):
    if mode == "phrase":
        emotion = emotion_task_top_result(text)
        emotion = emotion[0]
        return f"emoción más destacable de la frase: {emotion['label']}, puntuación: {round(emotion['score']*100,2)}%"
    elif mode == "text":
        pass
    elif mode == "poem":
        emotion_list = []
        score_list = []
        text = text.split(";")
        for verse in text:
            emotion = emotion_task_top_result(verse)
            emotion = emotion[0]
            emotion_list.append(emotion['label'])
            score_list.append(emotion['score'])
        return emotion_algorithm(emotion_list,score_list)

def emotion_algorithm(emotion_list,score_list):
    most_frequent_emotion = mode(emotion_list)
    scores = []
    for element in emotion_list:
        if element == most_frequent_emotion:
            scores.append(score_list[emotion_list.index(element)])
    total_score = (sum(scores)/len(scores))*100
    return f"emoción más destacable de la frase: {most_frequent_emotion}, puntuación: {round(total_score,2)}%"

def analyze_twitter(query):
    contents_list = []
    results_list = []
    label_list =[]
    sentiment_task = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment", tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment")
  
    for tweet in snstwitter.TwitterSearchScraper(query).get_items():
        contents_list.append(str(tweet.rawContent))
    for msg in contents_list:
        result = sentiment_task(msg)
        results_list.append(result[0])

    for result in results_list:
        label_list.append(result['label'])
    labels_count = {i:label_list.count(i) for i in label_list}

    positive = 0 if "positive" not in label_list else labels_count["positive"]
    neutral = 0 if "neutral" not in label_list else labels_count["neutral"] 
    negative = 0 if "negative" not in label_list else labels_count["negative"]

    return (positive,neutral,negative)


def make_youtube_request(part,order,textFormat,maxResults,videoId,pageToken,comments):

    request = youtube.commentThreads().list(
        part='snippet',
        order='relevance',
        textFormat='plainText',
        maxResults=maxResults,
        videoId=videoId,
        pageToken=pageToken
    )
    response = request.execute()
    for i in range(len(response['items'])):
        comments.append(response['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])
    pageToken = response['nextPageToken'] if 'nextPageToken' in response else ""
    return comments,pageToken

def analyse_youtube(id,maxResults):

    comments = []
    pageToken=None
    if maxResults > 100:
        while (maxResults > 0):
            comments,pageToken = make_youtube_request('snippet','relevance','plainText',maxResults,id,pageToken,comments)
            maxResults = maxResults-100
            if pageToken == "":
                break
    else:
        comments,pageToken = make_youtube_request('snippet','relevance','plainText',maxResults,id,pageToken,comments)
    print(len(comments))

    results_list = []
    label_list = []
    total_emotions = {'love':0,'admiration':0,'joy':0,'approval':0,'caring':0,'excitement':0,'amusement':0,'gratitude':0,'desire':0,'anger':0,'optimism':0,'disapproval':0,'grief':0,'annoyance':0,'pride':0,'curiosity':0,'neutral':0,'disgust':0,'disappointment':0,'realization':0,'fear':0,'relief':0,'confusion':0,'remorse':0,'embarrassment':0,'surprise':0,'sadness':0,'nervousness':0}
    topics = {"arts_&_culture":0,"fashion_&_style":0,"learning_&_educational":0,"science_&_technology":0,"business_&_entrepreneurs":0,"film_tv_&_video":0,"music":0,"sports":0,"celebrity_&_pop_culture":0,"fitness_&_health":0,"news_&_social_concern":0,"travel_&_adventure":0,"diaries_&_daily_life":0,"food_&_dining":0,"other_hobbies":0,"youth_&_student_life":0,"family":0,"gaming":0,"relationships":0}
    for text in comments:
        if len(text) < 1000:
            print(f"comment {comments.index(text)}")
            result = sentiment_task(text)
            results_list.append(result[0])
            text_topic = get_topics(text)
            for topic in text_topic:
                topics[topic] += text_topic[topic]

            text_emotions = emotion_task_top_result(text)
            for emotion in text_emotions:
                total_emotions[emotion['label']] += emotion['score']
        else:
            print("comment skipped due to oversize")

    for topic in topics:
        topics[topic] = topics[topic]/len(comments)
    
    for topic in topics:
        topics[topic] = float('%.2f'%(topics[topic]*100))

    for result in results_list:
        label_list.append(result['label'])
        labels_count = {i:label_list.count(i) for i in label_list}

    positive = 0 if "positive" not in label_list else labels_count["positive"]
    neutral = 0 if "neutral" not in label_list else labels_count["neutral"] 
    negative = 0 if "negative" not in label_list else labels_count["negative"]

    for emotion in total_emotions:
        total_emotions[emotion] = round(total_emotions[emotion]/len(comments),2)*100

    return (positive,neutral,negative,total_emotions,topics)

def scan_file_text(file,text):
    total_emotions = {'love':0,'admiration':0,'joy':0,'approval':0,'caring':0,'excitement':0,'amusement':0,'gratitude':0,'desire':0,'anger':0,'optimism':0,'disapproval':0,'grief':0,'annoyance':0,'pride':0,'curiosity':0,'neutral':0,'disgust':0,'disappointment':0,'realization':0,'fear':0,'relief':0,'confusion':0,'remorse':0,'embarrassment':0,'surprise':0,'sadness':0,'nervousness':0}
    topics = get_topics(text)
    for topic in topics:
        topics[topic] = float('%.1f'%(topics[topic]*100))
    if len(text) < 800:
        text_emotions = emotion_task_all_results(text)[0]
        for emotion in text_emotions:
            total_emotions[emotion['label']] += emotion['score']
        for emotion in total_emotions:
            total_emotions[emotion] = float('%.1f'%(total_emotions[emotion]*100))
        sentiment = classify_text_sentiment(text,"phrase")
    else:
        results = []
        text_divisions = []
        for letter in range(0, len(text), 800):
            text_divisions.append(text[letter:letter+800])
        for text_division in text_divisions:
            result = sentiment_task(text_division)
            results.append(result[0])

            text_emotions = emotion_task_all_results(text_division)[0]
            for emotion in text_emotions:
                total_emotions[emotion['label']] += emotion['score']
        for emotion in total_emotions:
            total_emotions[emotion] = float('%.1f'%(total_emotions[emotion]*100))
        sentiment = sentiment_algorithm(results)
        for emotion in total_emotions:
            total_emotions[emotion] = round(total_emotions[emotion]/len(text_divisions),2)
    file.close()
    os.remove(file.name)
    return sentiment,total_emotions,topics

def file_scan(mode,file):
    if mode == "single":
        with open(f"{file_uploads}/{file.filename}","r") as file:
            text = file.read()
            sentiment, total_emotions,topics = scan_file_text(file,text)
            return sentiment, total_emotions, topics
    elif mode == "multiple":
        with open(f"{file_uploads}/{file.filename}","r") as file:
            text = file.read()
            sentiment = classify_text_sentiment(text,"poem")
            texts = text.split(";")
            total_emotions = {'love':0,'admiration':0,'joy':0,'approval':0,'caring':0,'excitement':0,'amusement':0,'gratitude':0,'desire':0,'anger':0,'optimism':0,'disapproval':0,'grief':0,'annoyance':0,'pride':0,'curiosity':0,'neutral':0,'disgust':0,'disappointment':0,'realization':0,'fear':0,'relief':0,'confusion':0,'remorse':0,'embarrassment':0,'surprise':0,'sadness':0,'nervousness':0}
            topics = {"arts_&_culture":0,"fashion_&_style":0,"learning_&_educational":0,"science_&_technology":0,"business_&_entrepreneurs":0,"film_tv_&_video":0,"music":0,"sports":0,"celebrity_&_pop_culture":0,"fitness_&_health":0,"news_&_social_concern":0,"travel_&_adventure":0,"diaries_&_daily_life":0,"food_&_dining":0,"other_hobbies":0,"youth_&_student_life":0,"family":0,"gaming":0,"relationships":0}
            for text in texts:
                for key,score in get_topics(text).items():
                    topics[key] += score
                if len(text) < 800:
                    text_emotions = emotion_task_all_results(text)[0]
                    for emotion in text_emotions:
                        total_emotions[emotion['label']] += emotion['score']
                else:
                    pass
            for topic in topics:
                topics[topic] = topics[topic]/len(texts)
            for emotion in total_emotions:
                total_emotions[emotion] = total_emotions[emotion]/len(texts)
            for emotion in total_emotions:
                total_emotions[emotion] = float('%.1f'%(total_emotions[emotion]*100))
            for topic in topics:
                topics[topic] = float('%.2f'%(topics[topic]*100))
            return sentiment, total_emotions,topics
            

                
# Run the app
if __name__ == "__main__":
    app.run(debug=True)