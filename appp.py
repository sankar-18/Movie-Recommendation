import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests,io
import PIL.Image
from urllib.request import urlopen



with open('/Users/sankar/Documents/Movie_recommender/Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('/Users/sankar/Documents/Movie_recommender/Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

def movie_poster_fetcher(link):
    url_data=requests.get(link).text
    s_data=BeautifulSoup(url_data,"html.parser")
    imdb_dp=s_data.find("meta",property="og:image")
    movie_poster_link=imdb_dp.attrs["content"]
    u=urlopen(movie_poster_link)
    raw_data=u.read()
    image=PIL.Image.open(io.BytesIO(raw_data))
    image=image.resize((150,300),)
    st.image(image,use_column_width=False)



def get_movie_info(link):
    url_data=requests.get(link).text
    s_data=BeautifulSoup(url_data,"html.parser")
    imdb_content=s_data.find("meta",property="og:description")
    movie_description=imdb_content.attrs["content"]
    movie_description=str(movie_description).split(".")
    movie_director=movie_description[0]
    movie_cast=str(movie_description[1]).replace("With","Cast").strip()
    movie_story="Story:"+str(movie_description[2]).strip()+"."
    rating = s_data.find("div", class_="sc-7ab21ed2-3 dPVcnq")
    rating = str(rating).split('<div class="sc-7ab21ed2-3 dPVcnq')
    rating = str(rating[1]).split("</div>")
    rating = str(rating[0]).replace(''' "> ''', '').replace('">', '')
    movie_rating = 'Total Rating count: ' + rating
    return movie_director, movie_cast, movie_story, movie_rating


def KNN_Movie_Recommnder(test_point,k):
    target=[0 for item in movie_titles]
    model=KNearestNeighbours(data,target,test_point,k=k)
    model.fit()
    table=[]
    for i in model.indices:
        table.append(movie_titles[i][0],movie_titles[i][2],data[i][-1])
    print(table)
    return table

st.set_page_config(
   page_title="Movie Recommender System",
)

def run():
    img1=Image.open("/Users/sankar/Documents/Movie_recommender/Data/meta/logo.jpg")
    img1=img1.resize((250,250),)
    st.image(img1,use_column_width=False)
    st.title("Movie Recommendation System")
    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>***Data is based "IMDB 5000 Movie Dataset***</h4>''',
                unsafe_allow_html=True)
    genres=['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies=[title[0] for title in movie_titles]
    category=["--Select--","Movie Based","Genre Based"]
    cat_op=st.selectbox("Select Recoomendation Type",category)
    if cat_op == category[0]:
        st.warning("Please select any one Recommenndation type!!!")
    elif cat_op==category[1]:
        select_movie=st.selectbox("Select movie:(Recommendation will be based on this selection)",["--Select--"]+movies)
        img_dec=st.radio("want to fetch movie posters?",("Yes","No"))
        st.markdown('''<h4 style='text-align: left; color: #d73b5c;'*** Fetching a Movie Posters will take a time***</h4>''',
                    unsafe_allow_html=True)
        if img_dec=="No":
            if select_movie=="--Select--":
                st.warning("Please select any one movie!!!")
            else:
                no_of_recommendation=st.slider("Number of movie you want to Recommend:",min_value=5,max_value=20,step=1)
                genres=data[movies.index(select_movie)]
                test_point=genres
                table=KNN_Movie_Recommnder(test_point,no_of_recommendation+1)
                table.pop(0)
                c=0
                st.success("Heyyy!Here's some of movies from our recommendations,have a look")
                for movie,link,ratings in table:
                    c+=1
                    director,cast,story,total_rating=get_movie_info(link)
                    st.markdown(f"({c})[{movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rating)
                    st.markdown("IMDB Rating:"+str(total_rating)+"⭐")

        else:
            if select_movie=="--Select--":
                st.warning("Please select any one movie!!!")
            else:
                no_of_recommendation=st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
                genres=data[movies.index(select_movie)]
                test_points=genres
                table=KNN_Movie_Recommnder(test_points,no_of_recommendation+1)
                table.pop(0)
                c=0
                st.success("Heyyy!Here's some of movies from our recommendations,have a look")
                for movie,link,ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rating = get_movie_info(link)
                    st.markdown(f"({c})[{movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rating)
                    st.markdown("IMDB Rating:" + str(total_rating) + "⭐")
    elif cat_op==category[2]:
        select_genre=st.multiselect("Select Genre:",genres)
        img_dec = st.radio("want to fetch movie posters?", ("Yes", "No"))
        st.markdown(
            '''<h4 style='text-align: left; color: #d73b5c;'*** Fetching a Movie Posters will take a time***</h4>''',
            unsafe_allow_html=True)
        if img_dec == "No":
            if select_genre:
                imdb_score=st.slider("Choose Imdb score:",1,10,8)
                no_of_recommendation=st.number_input("Number of movies",min_value=5,max_value=20,step=1)
                test_point=[1 if genre in select_genre else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommnder(test_point, no_of_recommendation)
                c = 0
                st.success("Heyyy!Here's some of movies from our recommendations,have a look")
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    director, cast, story, total_rating = get_movie_info(link)
                    st.markdown(f"({c})[{movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rating)
                    st.markdown("IMDB Rating:" + str(total_rating) + "⭐")
        else:
            if select_genre:
                imdb_score = st.slider("Choose Imdb score:", 1, 10, 8)
                no_of_recommendation = st.number_input("Number of movies", min_value=5, max_value=20, step=1)
                test_point = [1 if genre in select_genre else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommnder(test_point, no_of_recommendation)
                c = 0
                st.success("Heyyy!Here's some of movies from our recommendations,have a look")
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rating = get_movie_info(link)
                    st.markdown(f"({c})[{movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rating)
                    st.markdown("IMDB Rating:" + str(total_rating) + "⭐")


run()







