import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import joblib
import tensorflow as tf
import lyricsgenius
import requests
from sklearn.metrics.pairwise import cosine_similarity
from feature_extraction.rhythm_extraction import extract_rhythm_features
from feature_extraction.lyrics_extraction import extract_lyrics_features
from models.rhythm_model import predict_rhythm_emotion
from models.lyrics_model import predict_lyrics_emotion
from groq import Groq


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
logging.basicConfig(level=logging.INFO)

# Absolute path to the uploads directory
UPLOADS_DIR = os.getenv('UPLOADS_DIR', 'C:\\Users\\nur_e\\EmoSync\\uploads')

genius_token = "QePVOK_EQXgFKSQa4IPOA5yT35ubQqaAxhaGcC56gc_PV-VdkNy0-oWqhcE4jI1N"  # Replace with your Genius API token
genius = lyricsgenius.Genius(genius_token)
tfidf_vectorizer = joblib.load('C:\\Users\\nur_e\\EmoSync\\models\\tfidf_vectorizer.pkl')
mlp_model = joblib.load('C:\\Users\\nur_e\\EmoSync\\models\\lyrics_mlp_model.pkl')

songs =  [
        {
            "id": 1,
            "title": "The Lazy Song",
            "formatted_title": " The Lazy Song",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/1.mp3"
        },
        {
            "id": 2,
            "title": "Best Day Of My Life",
            "formatted_title": "Best Day Of My Life",
            "image": "/static/images/cover/2.jpeg",
            "file_path": "/uploads/2.mp3"
        },
        {
            "id": 3,
            "title": "Cant Stop The Feeling",
            "formatted_title": "Cant Stop The Feeling",
            "image": "/static/images/cover/3.jpeg",
            "file_path": "/uploads/3.mp3"
        },
        {
            "id": 4,
            "title": "Sky Full Of Stars",
            "formatted_title": "Sky Full Of Stars",
            "image": "/static/images/cover/4.jpeg",
            "file_path": "/uploads/5.mp3"
        },
        {
            "id": 5,
            "title": "New Rules",
            "formatted_title": "New Rules",
            "image": "/static/images/cover/5.jpeg",
            "file_path": "/uploads/7.mp3"
        },
        {
            "id": 6,
            "title": "Uptown Funk",
            "formatted_title": "Uptown Funk",
            "image": "/static/images/cover/6.jpeg",
            "file_path": "/uploads/a008_uptown_funk.mp3"
        },
        {
            "id": 7,
            "title": "Sugar",
            "formatted_title": "Sugar",
            "image": "/static/images/cover/7.jpeg",
            "file_path": "/uploads/A009_Sugar.mp3"
        },
        {
            "id": 8,
            "title": "I Aint Worried",
            "formatted_title": "I Aint Worried",
            "image": "/static/images/cover/8.jpeg",
            "file_path": "/uploads/A010__I_Aint_Worried.mp3"
        },
        {
            "id": 9,
            "title": "I Feel It Coming",
            "formatted_title": "I Feel It Coming",
            "image": "/static/images/cover/9.jpeg",
            "file_path": "/uploads/A011__I_feel_it_coming.mp3"
        },
        {
            "id": 10,
            "title": "Happy",
            "formatted_title": "Happy",
            "image": "/static/images/cover/10.jpeg",
            "file_path": "/uploads/A012_Happy.mp3"
        },
        {
            "id": 11,
            "title": "Cheerleeder",
            "formatted_title": "Cheerleeder",
            "image": "/static/images/cover/11.jpeg",
            "file_path": "/uploads/A014_Cheerleeder.mp3"
        },
        {
            "id": 12,
            "title": "Shape Of You",
            "formatted_title": "Shape Of You",
            "image": "/static/images/cover/12.jpeg",
            "file_path": "/uploads/A015_Shape_of_You.mp3"
        },
        {
            "id": 13,
            "title": "Sunflower",
            "formatted_title": "Sunflower",
            "image": "/static/images/cover/13.jpeg",
            "file_path": "/uploads/A016_Sunflower.mp3"
        },
        {
            "id": 14,
            "title": "Better Days",
            "formatted_title": "Better Days",
            "image": "/static/images/cover/14.jpeg",
            "file_path": "/uploads/A017_Better_Days.mp3"
        },
        {
            "id": 15,
            "title": "Futureland Ace",
            "formatted_title": "Futureland Ace",
            "image": "/static/images/cover/15.jpeg",
            "file_path": "/uploads/A018_UTURELAND_ACE.mp3"
        },
        {
            "id": 16,
            "title": "Shake It Off",
            "formatted_title": "Shake It Off",
            "image": "/static/images/cover/16.jpeg",
            "file_path": "/uploads/A019__Shake_It_Off.mp3"
        },
        {
            "id": 17,
            "title": "FallenLeaves",
            "formatted_title": "Fallenleaves",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A020_FallenLeaves.mp3"
        },
        {
            "id": 18,
            "title": "Red Flag",
            "formatted_title": "Red Flag",
            "image": "/static/images/cover/18.jpeg",
            "file_path": "/uploads/A021_Red_Flag.mp3"
        },
        {
            "id": 19,
            "title": "Breathe",
            "formatted_title": "Breathe",
            "image": "/static/images/cover/19.jpeg",
            "file_path": "/uploads/A022_Breathe.mp3"
        },
        {
            "id": 20,
            "title": "Lets Get It Started",
            "formatted_title": "Lets Get It Started",
            "image": "/static/images/cover/20.jpeg",
            "file_path": "/uploads/A023_Lets_Get_It_Started.mp3"
        },
        {
            "id": 21,
            "title": "Cut Me Out",
            "formatted_title": "Cut Me Out",
            "image": "/static/images/cover/21.jpeg",
            "file_path": "/uploads/A024_Cut_Me_Out.mp3"
        },
        {
            "id": 22,
            "title": "One In A Million",
            "formatted_title": "One In A Million",
            "image": "/static/images/cover/22.jpeg",
            "file_path": "/uploads/A025_One_In_A_Million.mp3"
        },
        {
            "id": 23,
            "title": "You Are So Beautiful ",
            "formatted_title": "You Are So Beautiful",
            "image": "/static/images/cover/23.jpeg",
            "file_path": "/uploads/A026_Escape_The_Fate-_You_Are_So_Beautiful-_Lyrics.mp3"
        },
        {
            "id": 24,
            "title": "Right Round",
            "formatted_title": "Right Round",
           "image": "/static/images/cover/24.jpeg",
            "file_path": "/uploads/A027_Flo_Rida_-_Right_Round_Lyrics.mp3"
        },
        {
            "id": 25,
            "title": "Radioactive",
            "formatted_title": "Radioactive",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A028_RADIOACTIVE.mp3"
        },
        {
            "id": 26,
            "title": "Wavin Flag",
            "formatted_title": "Wavin Flag ",
            "image": "/static/images/cover/25.jpeg",
            "file_path": "/uploads/a029__Wavin_Flag_Official_Audio.mp3"
        },
        {
            "id": 27,
            "title": "I Kissed A Girl",
            "formatted_title": "I Kissed A Girl",
            "image": "/static/images/cover/27.jpeg",
            "file_path": "/uploads/a031_I_Kissed_a_Girl_Audio.mp3"
        },
        {
            "id": 28,
            "title": "Dancing With Tears In My Eyes",
            "formatted_title": "Dancing With Tears In My Eyes",
            "image": "/static/images/cover/28.jpeg",
            "file_path": "/uploads/a032_dancing_with_tears_in_my_eyes.mp3"
        },
        {
            "id": 29,
            "title": "Just Dance",
            "formatted_title": " Just Dance",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/a034-_Just_Dance_ft._Colby_ODonis_Lyrics.mp3"
        },
        {
            "id": 30,
            "title": "Lets Get Crazy",
            "formatted_title": " Lets Get Crazy",
            "image": "/static/images/cover/30.jpeg",
            "file_path": "/uploads/a035_Lets_Get_Crazy_Hannah_Montana_Lyrics.mp3"
        },
        {
            "id": 31,
            "title": "Best Song Ever",
            "formatted_title": "Best Song Ever",
            "image": "/static/images/cover/31.jpeg",
            "file_path": "/uploads/a036__Best_Song_Ever_Audio.mp3"
        },
        {
            "id": 32,
            "title": "Live While Were Young",
            "formatted_title": "Live While Were Young",
            "image": "/static/images/cover/32.jpeg",
            "file_path": "/uploads/A037_live_while_were_young_lyrics.mp3"
        },
        {
            "id": 33,
            "title": "What Makes You Beautiful",
            "formatted_title": "What Makes You Beautiful",
           "image": "/static/images/cover/33.jpeg",
            "file_path": "/uploads/A038_What_Makes_You_Beautiful.mp3"
        },
        {
            "id": 34,
            "title": "All The Right Moves",
            "formatted_title": "All The Right Moves",
            "image": "/static/images/cover/34.jpeg",
            "file_path": "/uploads/A039_All_the_right_moves.mp3"
        },
        {
            "id": 35,
            "title": "I Wanna Dance With Somebody Lyrics",
            "formatted_title": "I Wanna Dance With Somebody Lyrics",
            "image": "/static/images/cover/35.jpeg",
            "file_path": "/uploads/A040__I_Wanna_Dance_With_Somebody_Lyrics.mp3"
        },
        {
            "id": 36,
            "title": "Wake Me Up Before You Go Go",
            "formatted_title": "Wake Me Up Before You Go Go ",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A041_Wake_Me_Up_Before_You_Go-Go_Lyrics.mp3"
        },
        {
            "id": 37,
            "title": "Twist Shout",
            "formatted_title": "Twist  Shout",
            "image": "/static/images/cover/46.jpeg",
            "file_path": "/uploads/A042__Twist__Shout_Lyrics.mp3"
        },
        {
            "id": 38,
            "title": "Dynamite",
            "formatted_title": " Dynamite ",
            "image": "/static/images/cover/38.jpeg",
            "file_path": "/uploads/a043__Dynamite_Lyrics.mp3"
        },
        {
            "id": 39,
            "title": "California Girls",
            "formatted_title": "California Girls",
            "image": "/static/images/cover/39.jpeg",
            "file_path": "/uploads/A044_California_Girls.mp3"
        },
        {
            "id": 40,
            "title": "Cruel Summer",
            "formatted_title": "Cruel Summer",
            "image": "/static/images/cover/40.jpeg",
            "file_path": "/uploads/a045_cruel_summer.mp3"
        },
        {
            "id": 41,
            "title": "Single Ladies",
            "formatted_title": " Single Ladies",
            "image": "/static/images/cover/41.jpeg",
            "file_path": "/uploads/a046_single_ladies.mp3"
        },
        {
            "id": 42,
            "title": "Staying Alive",
            "formatted_title": " Staying Alive",
            "image": "/static/images/cover/42.jpeg",
            "file_path": "/uploads/a047_staying_alive.mp3"
        },
        {
            "id": 43,
            "title": "Dancing Queen",
            "formatted_title": " Dancing Queen",
            "image": "/static/images/cover/43.jpeg",
            "file_path": "/uploads/a048_dancing_queen.mp3"
        },
        {
            "id": 44,
            "title": "Uptown Girl",
            "formatted_title": " Uptown Girl",
            "image": "/static/images/cover/44.jpeg",
            "file_path": "/uploads/a049_uptown_girl.mp3"
        },
        {
            "id": 45,
            "title": "Cake By The Ocean",
            "formatted_title": "Cake By The Ocean",
            "image": "/static/images/cover/45.jpeg",
            "file_path": "/uploads/a050-_Cake_By_The_Ocean.mp3"
        },
        {
            "id": 46,
            "title": "Girlfriend",
            "formatted_title": "Girlfriend ",
            "image": "/static/images/cover/46.jpeg",
            "file_path": "/uploads/A052_-_Girlfriend_Official_Video.mp3"
        },
        {
            "id": 47,
            "title": "Its My Life",
            "formatted_title": "Its My Life",
            "image": "/static/images/cover/47.jpeg",
            "file_path": "/uploads/A053__Its_My_Life_Lyrics.mp3"
        },
        {
            "id": 48,
            "title": "Bring Me To Life",
            "formatted_title": " Bring Me To Life  ",
            "image": "/static/images/cover/48.jpeg",
            "file_path": "/uploads/a054_Bring_Me_To_Life_Official_HD_Music_Video.mp3"
        },
        {
            "id": 49,
            "title": "Everybodys Fool",
            "formatted_title": "Everybodys Fool ",
            "image": "/static/images/cover/49.jpeg",
            "file_path": "/uploads/A055_Everybodys_Fool_lyrics.mp3"
        },
        {
            "id": 50,
            "title": "Ignorance",
            "formatted_title": "Ignorance",
            "image": "/static/images/cover/51.jpeg",
            "file_path": "/uploads/A056_Ignorance_-_Paramore_LYRICS.mp3"
        },
        {
            "id": 51,
            "title": "Demons",
            "formatted_title": "Demons",
            "image": "/static/images/cover/51.jpeg",
            "file_path": "/uploads/A057-_Demons.mp3"
        },
        {
            "id": 52,
            "title": "Numb",
            "formatted_title": "Numb",
            "image": "/static/images/cover/52.jpeg",
            "file_path": "/uploads/A058_NUMB.mp3"
        },
        {
            "id": 53,
            "title": "Decode",
            "formatted_title": "Decode",
            "image": "/static/images/cover/53.jpeg",
            "file_path": "/uploads/A059_DECODE.mp3"
        },
        {
            "id": 54,
            "title": "Stab My Back",
            "formatted_title": "Picture To Burn",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A060_Picture_to_burn.mp3"
        },
        {
            "id": 55,
            "title": "a061_stab_my_back",
            "formatted_title": " Stab My Back",
            "image": "/static/images/cover/55.jpeg",
            "file_path": "/uploads/a061_stab_my_back.mp3"
        },
        {
            "id": 56,
            "title": "Ultranumb",
            "formatted_title": "Ultranumb",
            "image": "/static/images/cover/56.jpeg",
            "file_path": "/uploads/a062_ultranumb.mp3"
        },
        {
            "id": 57,
            "title": "I Will Not Bow",
            "formatted_title": " I Will Not Bow",
            "image": "/static/images/cover/57.jpeg",
            "file_path": "/uploads/a063_i_will_not_bow.mp3"
        },
        {
            "id": 58,
            "title": "Into The Nothing",
            "formatted_title": " Into The Nothing",
            "image": "/static/images/cover/58.jpeg",
            "file_path": "/uploads/a064_into_the_nothing.mp3"
        },
        {
            "id": 59,
            "title": "Warrior",
            "formatted_title": "Warrior",
            "image": "/static/images/cover/59.jpeg",
            "file_path": "/uploads/A065_Warrior.mp3"
        },
        {
            "id": 60,
            "title": "In The End",
            "formatted_title": "In The End",
            "image": "/static/images/cover/60.jpeg",
            "file_path": "/uploads/A066_In_the_end.mp3"
        },
        {
            "id": 61,
            "title": "Edge and Pearl",
            "formatted_title": "Edge And Pearl",
            "image": "/static/images/cover/61.jpeg",
            "file_path": "/uploads/a067_Edge_and_Pearl.mp3"
        },
        {
            "id": 62,
            "title": "Im Picky",
            "formatted_title": "Im Picky ",
           "image": "/static/images/cover/62.jpeg",
            "file_path": "/uploads/a068Im_Picky_Lyrics.mp3"
        },
        {
            "id": 63,
            "title": "Where Did The Angels Go",
            "formatted_title": " Where Did The Angels Go",
           "image": "/static/images/cover/63.jpeg",
            "file_path": "/uploads/a069__Where_Did_The_Angels_Go_Lyrics_on_screen_HD.mp3"
        },
        {
            "id": 64,
            "title": "Riot",
            "formatted_title": "Riot ",
            "image": "/static/images/cover/64.jpeg",
            "file_path": "/uploads/a072__Riot_Lyrics.mp3"
        },
        {
            "id": 65,
            "title": "Teenagers",
            "formatted_title": " Teenagers ",
            "image": "/static/images/cover/65.jpeg",
            "file_path": "/uploads/a073__Teenagers_lyrics.mp3"
        },
        {
            "id": 66,
            "title": "Night Of Hunter",
            "formatted_title": " Night Of Hunter",
            "image": "/static/images/cover/66.jpeg",
            "file_path": "/uploads/a074_night_of_hunter.mp3"
        },
        {
            "id": 67,
            "title": "Force",
            "formatted_title": " Force",
            "image": "/static/images/cover/67.jpeg",
            "file_path": "/uploads/a075_Force.mp3"
        },
        {
            "id": 68,
            "title": "You Dont know Me",
            "formatted_title": "You Dont Know Me",
            "image": "/static/images/cover/68.jpeg",
            "file_path": "/uploads/a076_you_dont_know_me.mp3"
        },
        {
            "id": 69,
            "title": "War Pigs",
            "formatted_title": " War Pigs",
            "image": "/static/images/cover/69.jpeg",
            "file_path": "/uploads/a087_War_Pigs.mp3"
        },
        {
            "id": 70,
            "title": "London Calling",
            "formatted_title": " London Calling",
            "image": "/static/images/cover/70.jpeg",
            "file_path": "/uploads/a090_london_Calling.mp3"
        },
        {
            "id": 71,
            "title": "Prison Song",
            "formatted_title": " Prison Song ",
            "image": "/static/images/cover/71.jpeg",
            "file_path": "/uploads/a092__Prison_Song_Official_Audio.mp3"
        },
        {
            "id": 72,
            "title": "Lose Yourself",
            "formatted_title": "Lose Yourself ",
            "image": "/static/images/cover/72.jpeg",
            "file_path": "/uploads/a094__Lose_Yourself_Lyrics.mp3"
        },
        {
            "id": 73,
            "title": "Killing In The Name",
            "formatted_title": "Killing In The Name",
            "image": "/static/images/cover/73.jpeg",
            "file_path": "/uploads/a095_Killing_In_The_Name.mp3"
        },
        {
            "id": 74,
            "title": "a096_eye_of_the_tiger",
            "formatted_title": "Eye Of The Tiger",
            "image": "/static/images/cover/74.jpeg",
            "file_path": "/uploads/a096_eye_of_the_tiger.mp3"
        },
        {
            "id": 75,
            "title": "Dead Bodies Everywhere",
            "formatted_title": "Dead Bodies Everywhere",
           "image": "/static/images/cover/75.jpeg",
            "file_path": "/uploads/a097__Dead_Bodies_Everywhere_Lyrics_on_Screen.mp3"
        },
        {
            "id": 76,
            "title": "Last Resort",
            "formatted_title": "Last Resort",
            "image": "/static/images/cover/76.jpeg",
            "file_path": "/uploads/a098_Last_Resort.mp3"
        },
        {
            "id": 77,
            "title": "Bring Your Whole Crew",
            "formatted_title": "Bring Your Whole Crew",
            "image": "/static/images/cover/77.jpeg",
            "file_path": "/uploads/a099_Bring_Your_Whole_Crew.mp3"
        },
        {
            "id": 78,
            "title": "I Fucking Hate You",
            "formatted_title": " I Fucking Hate You",
            "image": "/static/images/cover/78.jpeg",
            "file_path": "/uploads/a100_i_fucking_hate_you.mp3"
        },
        {
            "id": 79,
            "title": "How Far Ill Go",
            "formatted_title": " How Far Ill Go ",
            "image": "/static/images/cover/179.jpeg",
            "file_path": "/uploads/A101___How_Far_Ill_Go_Lirik.mp3"
        },
        {
            "id": 80,
            "title": "Photograph",
            "formatted_title": "Photograph ",
            "image": "/static/images/cover/80.jpeg",
            "file_path": "/uploads/A102__Photograph_Lyrics.mp3"
        },
        {
            "id": 81,
            "title": "Flashlight",
            "formatted_title": "Flashlight ",
            "image": "/static/images/cover/81.jpeg",
            "file_path": "/uploads/A103__Flashlight_-_Jessie_J_Lyrics.mp3"
        },
        {
            "id": 82,
            "title": "All Of Me",
            "formatted_title": "All Of Me",
            "image": "/static/images/cover/81.jpeg",
            "file_path": "/uploads/A104__All_of_meLyrics.mp3"
        },
        {
            "id": 83,
            "title": "7 Years",
            "formatted_title": " 7 Years ",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A105__7_Years_Lyrics.mp3"
        },
        {
            "id": 84,
            "title": "Only Love Can Hurt Like This ",
            "formatted_title": "Only Love Can Hurt Like This ",
            "image": "/static/images/cover/84.jpeg",
            "file_path": "/uploads/A106_Only_Love_Can_Hurt_Like_This_Lyrics.mp3"
        },
        {
            "id": 85,
            "title": "Dandelions",
            "formatted_title": " Dandelions ",
            "image": "/static/images/cover/85.jpeg",
            "file_path": "/uploads/A107_Dandelions_Lyrics.mp3"
        },
        {
            "id": 86,
            "title": "A Million Dreams",
            "formatted_title": "A Million Dreams ",
            "image": "/static/images/cover/86.jpeg",
            "file_path": "/uploads/A108_A_Million_Dreams_Lyric_Video_HD_1.mp3"
        },
        {
            "id": 87,
            "title": "Sad Song",
            "formatted_title": "Sad Song",
            "image": "/static/images/cover/87.jpeg",
            "file_path": "/uploads/A109_Sad_Song_Lyric_Video_ft._Elena_Coats.mp3"
        },
        {
            "id": 88,
            "title": " My Love ",
            "formatted_title": " My Love ",
            "image": "/static/images/cover/88.jpeg",
            "file_path": "/uploads/A110__My_Love_Lyrics.mp3"
        },
        {
            "id": 89,
            "title": "See You Again",
            "formatted_title": " See You Again",
            "image": "/static/images/cover/89.jpeg",
            "file_path": "/uploads/A111-_See_You_Again_ft._Charlie_Puth_Lyrics.mp3"
        },
        {
            "id": 90,
            "title": "Story Of A Girl",
            "formatted_title": "Story Of A Girl",
            "image": "/static/images/cover/90.jpeg",
            "file_path": "/uploads/A112Story_of_a_girl_lyrics_-_Nine_Days.mp3"
        },
        {
            "id": 91,
            "title": "Faded ",
            "formatted_title": "Faded ",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/A113_-_Faded_Lyrics.mp3"
        },
        {
            "id": 92,
            "title": "Total Eclipse Of The Heart",
            "formatted_title": "Total Eclipse Of The Heart",
            "image": "/static/images/cover/91.jpeg",
            "file_path": "/uploads/A114_Total_Eclipse_of_the_Heart_Official_Lyric_Video.mp3"
        },
        {
            "id": 93,
            "title": "Heart Attack",
            "formatted_title": " Heart Attack ",
            "image": "/static/images/cover/92.jpeg",
            "file_path": "/uploads/A115_Heart_Attack_Lyrics.mp3"
        },
        {
            "id": 94,
            "title": "Used To Be Young",
            "formatted_title": "Used To Be Young",
            "image": "/static/images/cover/93.jpeg",
            "file_path": "/uploads/a116-_Used_To_Be_Young_Official_Video_1.mp3"
        },
        {
            "id": 95,
            "title": "Fire On Fire",
            "formatted_title": " Fire On Fire",
            "image": "/static/images/cover/95.jpeg",
            "file_path": "/uploads/a117-_Fire_On_Fire_From_Watership_Down.mp3"
        },
        {
            "id": 96,
            "title": "Take Me Away",
            "formatted_title": " Take Me Away",
            "image": "/static/images/cover/96.jpeg",
            "file_path": "/uploads/A118_Take_Me_Away.mp3"
        },
        {
            "id": 97,
            "title": "Here With Me ",
            "formatted_title": "  Here With Me  ",
            "image": "/static/images/cover/97.jpeg",
            "file_path": "/uploads/a119-_Here_With_Me_Official_Audio.mp3"
        },
        {
            "id": 98,
            "title": " Use Somebody ",
            "formatted_title": "  Use Somebody ",
            "image": "/static/images/cover/98.jpeg",
            "file_path": "/uploads/a120__Use_Somebody_Kings_of_Leon_cover.mp3"
        },
        {
            "id": 99,
            "title": "Train Wreck ",
            "formatted_title": "Train Wreck ",
            "image": "/static/images/cover/99.jpeg",
            "file_path": "/uploads/a121-_Train_Wreck_Lyrics.mp3"
        },
        {
            "id": 100,
            "title": "Roads Untraveled ",
            "formatted_title": "Roads Untraveled ",
            "image": "/static/images/cover/100.jpeg",
            "file_path": "/uploads/a122_roads_untraveled_lyrics.mp3"
        },
        {
            "id": 101,
            "title": "Cant Forget You",
            "formatted_title": "Cant Forget You",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/a123_cant_forget_you.mp3"
        },
        {
            "id": 102,
            "title": "Hero Of War",
            "formatted_title": "  Hero Of War    ",
            "image": "/static/images/cover/1.jpeg",
            "file_path": "/uploads/a124-_Hero_Of_War__With_Lyrics_.mp3"
        },
        {
            "id": 103,
            "title": "How Could This Happen To Me",
            "formatted_title": " How Could This Happen To Me ",
            "image": "/static/images/cover/103.jpeg",
            "file_path": "/uploads/a126_How_Could_This_Happen_To_Me_with_lyrics.mp3"
        },
        {
            "id": 104,
            "title": "Lonely Day",
            "formatted_title": "Lonely Day ",
           "image": "/static/images/cover/104.jpeg",
            "file_path": "/uploads/a127-_Lonely_day_lyrics.mp3"
        },
        {
            "id": 105,
            "title": "Love Story ",
            "formatted_title": "Love Story ",
            "image": "/static/images/cover/105.jpeg",
            "file_path": "/uploads/a128-_Love_Story_Audio.mp3"
        },
        {
            "id": 106,
            "title": "a129_Itll_Be_Okay",
            "formatted_title": "Itll Be Okay",
            "image": "/static/images/cover/106.jpeg",
            "file_path": "/uploads/a129_Itll_Be_Okay.mp3"
        },
        {
            "id": 107,
            "title": "Home",
            "formatted_title": " Home ",
            "image": "/static/images/cover/107.jpeg",
            "file_path": "/uploads/a131_Three_Days_Grace_-_Home_Lyrics.mp3"
        },
        {
            "id": 108,
            "title": "Touched",
            "formatted_title": " Touched",
            "image": "/static/images/cover/108.jpeg",
            "file_path": "/uploads/a132_Touched.mp3"
        },
        {
            "id": 109,
            "title": "Easy On Me",
            "formatted_title": "Easy On Me",
            "image": "/static/images/cover/109.jpeg",
            "file_path": "/uploads/a133_Easy_On_Me_Official_Lyric_Video.mp3"
        },
        {
            "id": 110,
            "title": "Perfect",
            "formatted_title": "Perfect",
            "image": "/static/images/cover/110.jpeg",
            "file_path": "/uploads/a134_-_Perfect_Official_Lyric_Video.mp3"
        },
        {
            "id": 111,
            "title": "For The Love Of A Daughter",
            "formatted_title": "For The Love Of A Daughter",
            "image": "/static/images/cover/111.jpeg",
            "file_path": "/uploads/a135__For_the_Love_of_a_Daughter_Lyrics_-_Demi_Lovato.mp3"
        },
        {
            "id": 112,
            "title": "Yesterday",
            "formatted_title": "Yesterday ",
            "image": "/static/images/cover/112.jpeg",
            "file_path": "/uploads/a136-_Yesterday_Lyrics.mp3"
        },
        {
            "id": 113,
            "title": "Hello",
            "formatted_title": "Hello Evanescence ",
            "image": "/static/images/cover/113.jpeg",
            "file_path": "/uploads/a137_Hello-Evanescence-Lyrics.mp3"
        },
        {
            "id": 114,
            "title": "Home",
            "formatted_title": "Home",
            "image": "/static/images/cover/114.jpeg",
            "file_path": "/uploads/a138_home.mp3"
        },
        {
            "id": 115,
            "title": "Say Something",
            "formatted_title": "Say Something",
            "image": "/static/images/cover/115.jpeg",
            "file_path": "/uploads/A139-_Say_Something_Lyrics.mp3"
        },
        {
            "id": 116,
            "title": "Angels",
            "formatted_title": "Angels ",
            "image": "/static/images/cover/116.jpeg",
            "file_path": "/uploads/a140-_Angels_Lyrics.mp3"
        },
        {
            "id": 117,
            "title": "Everybody Hurts",
            "formatted_title": " Everybody Hurts ",
            "image": "/static/images/cover/117.jpeg",
            "file_path": "/uploads/A141-_Everybody_Hurts_Lyrics.mp3"
        },
        {
            "id": 118,
            "title": "Sacrifice",
            "formatted_title": " Sacrifice ",
            "image": "/static/images/cover/118.jpeg",
            "file_path": "/uploads/A142_Sacrifice_Lyrics_1.mp3"
        },
        {
            "id": 119,
            "title": "Creep Radiohead ",
            "formatted_title": "Creep Radiohead ",
            "image": "/static/images/cover/119.jpeg",
            "file_path": "/uploads/A144_Creep_-_Radiohead_Lyrics.mp3"
        },
        {
            "id": 120,
            "title": "What Was I Made For",
            "formatted_title": " What Was I Made For",
            "image": "/static/images/cover/120.jpeg",
            "file_path": "/uploads/A145_-_What_Was_I_Made_For__Official_Lyric_Video.mp3"
        },
        {
            "id": 121,
            "title": "Dance With My Father",
            "formatted_title": "Dance With My Father",
            "image": "/static/images/cover/121.jpeg",
            "file_path": "/uploads/A146__Dance_With_My_Father_Lyrics_-_Luther_Vandross.mp3"
        },
        {
            "id": 122,
            "title": "Mad World",
            "formatted_title": " Mad World",
            "image": "/static/images/cover/122.jpeg",
            "file_path": "/uploads/A147_Mad_World_-_Gary_Jules_Lyrics.mp3"
        },
        {
            "id": 123,
            "title": "When I Was Your Man",
            "formatted_title": "When I Was Your Man",
            "image": "/static/images/cover/123.jpeg",
            "file_path": "/uploads/a148-_When_I_Was_Your_Man.mp3"
        },
        {
            "id": 124,
            "title": "Broken Strings",
            "formatted_title": "Broken Strings ",
            "image": "/static/images/cover/124.jpeg",
            "file_path": "/uploads/A149-Broken_Strings_Lyrics.mp3"
        },
        {
            "id": 125,
            "title": "Gloomy Sunday",
            "formatted_title": "Gloomy Sunday",
            "image": "/static/images/cover/125.jpeg",
            "file_path": "/uploads/A150_Gloomy_Sunday.mp3"
        },
        {
            "id": 126,
            "title": " A Thousand Years",
            "formatted_title": " A Thousand Years ",
            "image": "/static/images/cover/126.jpeg",
            "file_path": "/uploads/a151-_A_Thousand_Years_Official_Music_Video.mp3"
        },
        {
            "id": 127,
            "title": "Heather",
            "formatted_title": "Heather",
            "image": "/static/images/cover/127.jpeg",
            "file_path": "/uploads/a152_-_Heather.mp3"
        },
        {
            "id": 128,
            "title": "a153_-_Let_It_Go",
            "formatted_title": "Let It Go",
            "image": "/static/images/cover/128.jpeg",
            "file_path": "/uploads/a153_-_Let_It_Go.mp3"
        },
        {
            "id": 129,
            "title": "Golden Hour",
            "formatted_title": " Golden Hour  ",
            "image": "/static/images/cover/130.jpeg",
            "file_path": "/uploads/a154_golden_hour_official_music_video.mp3"
        },
        {
            "id": 130,
            "title": "Night Changes",
            "formatted_title": " Night Changes",
            "image": "/static/images/cover/130.jpeg",
            "file_path": "/uploads/a155_Night_Changes.mp3"
        },
        {
            "id": 131,
            "title": "To The Bone",
            "formatted_title": " To The Bone",
            "image": "/static/images/cover/131.jpeg",
            "file_path": "/uploads/a156-_To_The_Bone.mp3"
        },
        {
            "id": 132,
            "title": "Sunset Lover",
            "formatted_title": "Sunset Lover",
            "image": "/static/images/cover/132.jpeg",
            "file_path": "/uploads/a157_Sunset_Lover.mp3"
        },
        {
            "id": 133,
            "title": "a158_Fight_Song_Lyrics",
            "formatted_title": "Fight Song ",
            "image": "/static/images/cover/133.jpeg",
            "file_path": "/uploads/a158_Fight_Song_Lyrics.mp3"
        },
        {
            "id": 134,
            "title": "Enchanted",
            "formatted_title": "Enchanted",
            "image": "/static/images/cover/134.jpeg",
            "file_path": "/uploads/a159_Enchanted_Taylors_Version_Lyric_Video.mp3"
        },
        {
            "id": 135,
            "title": "Paris",
            "formatted_title": "Paris",
            "image": "/static/images/cover/135.jpeg",
            "file_path": "/uploads/a160_-_Paris_Official_Lyric_Video.mp3"
        },
        {
            "id": 136,
            "title": "The Moon Song",
            "formatted_title": " The Moon Song",
            "image": "/static/images/cover/136.jpeg",
            "file_path": "/uploads/a162_The_Moon_Song.mp3"
        },
        {
            "id": 137,
            "title": "On An Ocean",
            "formatted_title": "On An Ocean",
            "image": "/static/images/cover/137.jpeg",
            "file_path": "/uploads/a163_On_An_Ocean.mp3"
        },
        {
            "id": 138,
            "title": "Paint The Sky With Stars",
            "formatted_title": " Paint The Sky With Stars",
            "image": "/static/images/cover/138.jpeg",
            "file_path": "/uploads/a164_Paint_The_Sky_With_Stars.mp3"
        },
        {
            "id": 139,
            "title": "Sunrise",
            "formatted_title": "Sunrise",
            "image": "/static/images/cover/139.jpeg",
            "file_path": "/uploads/a165_Sunrise.mp3"
        },
        {
            "id": 140,
            "title": "Thank You Stars",
            "formatted_title": "Thank You Stars",
            "image": "/static/images/cover/140.jpeg",
            "file_path": "/uploads/a166_Thank_You_Stars.mp3"
        },
        {
            "id": 141,
            "title": "The Boy From Ipanema",
            "formatted_title": " The Boy From Ipanema",
            "image": "/static/images/cover/141.jpeg",
            "file_path": "/uploads/a167_The_Boy_From_Ipanema.mp3"
        },
        {
            "id": 142,
            "title": "Those Sweet Words",
            "formatted_title": " Those Sweet Words",
            "image": "/static/images/cover/142.jpeg",
            "file_path": "/uploads/a168_those_sweet_words.mp3"
        },
        {
            "id": 143,
            "title": "Country Comfort",
            "formatted_title": "Country Comfort",
            "image": "/static/images/cover/143.jpeg",
            "file_path": "/uploads/a170_Country_Comfort.mp3"
        },
        {
            "id": 144,
            "title": "Thats What Friends Are For",
            "formatted_title": "Thats What Friends Are For ",
            "image": "/static/images/cover/144.jpeg",
            "file_path": "/uploads/a172_Thats_What_Friends_Are_For_Lyrics.mp3"
        },
        {
            "id": 146,
            "title": "May It Be",
            "formatted_title": " May It Be ",
            "image": "/static/images/cover/146.jpeg",
            "file_path": "/uploads/a174_-_May_It_Be_Official_Lyric_Video.mp3"
        },
        {
            "id": 147,
            "title": "Albedo 0.39",
            "formatted_title": " Albedo 0.39",
            "image": "/static/images/cover/147.jpeg",
            "file_path": "/uploads/a175-_Albedo_0.39.mp3"
        },
        {
            "id": 148,
            "title": "Sleeping Child",
            "formatted_title": " Sleeping Child  Michael Learns To Rock ",
            "image": "/static/images/cover/148.jpeg",
            "file_path": "/uploads/a177-Sleeping_Child_-_Music_Travel_Love__Michael_Learns_to_Rock_Official_Video.mp3"
        },
        {
            "id": 149,
            "title": "Journey Of The Angels",
            "formatted_title": " Journey Of The Angels ",
            "image": "/static/images/cover/149.jpeg",
            "file_path": "/uploads/a177-_Journey_of_the_Angels_Lyric_Video.mp3"
        },
        {
            "id": 150,
            "title": "Top Of The World",
            "formatted_title": "Top Of The World",
            "image": "/static/images/cover/150.jpeg",
            "file_path": "/uploads/a178Top_Of_The_World_Acoustic_Duo_Oxfordshire_Weddings__Events.mp3"
        },
        {
            "id": 151,
            "title": "a180_How_Could_Anyone",
            "formatted_title": "How Could Anyone",
            "image": "/static/images/cover/151.jpeg",
            "file_path": "/uploads/a180_How_Could_Anyone.mp3"
        },
        {
            "id": 152,
            "title": "I Still Havent Found What Im Looking For   ",
            "formatted_title": "I Still Havent Found What Im Looking For   ",
            "image": "/static/images/cover/152.jpeg",
            "file_path": "/uploads/a180_I_Still_Havent_Found_What_Im_Looking_For_-_Music_Travel_Love_Cover.mp3"
        },
        {
            "id": 153,
            "title": "Love Is Where You Are",
            "formatted_title": "Love Is Where You Are",
            "image": "/static/images/cover/153.jpeg",
            "file_path": "/uploads/a181_Love_Is_Where_You_Are_-_Kadesh.mp3"
        },
        {
            "id": 154,
            "title": "Peace Train",
            "formatted_title": "Peace Train",
            "image": "/static/images/cover/154.jpeg",
            "file_path": "/uploads/a183_eace_Train.mp3"
        },
        {
            "id": 155,
            "title": "But Beautiful",
            "formatted_title": " But Beautiful  ",
            "image": "/static/images/cover/155.jpeg",
            "file_path": "/uploads/a184_-_But_Beautiful_Studio_Video.mp3"
        },
        {
            "id": 156,
            "title": "I Am The Earth",
            "formatted_title": "I Am The Earth ",
            "image": "/static/images/cover/156.jpeg",
            "file_path": "/uploads/a185_I_Am_The_Earth_Lyrics.mp3"
        },
        {
            "id": 157,
            "title": "Friends Are Quite Angels",
            "formatted_title": "Friends Are Quite Angels",
            "image": "/static/images/cover/157.jpeg",
            "file_path": "/uploads/a186_friends_are_quite_angels.mp3"
        },
        {
            "id": 159,
            "title": "Heather",
            "formatted_title": " Heather",
            "image": "/static/images/cover/159.jpeg",
            "file_path": "/uploads/a187_Conan_Gray_-_Heather.mp3"
        },
        {
            "id": 160,
            "title": "Careless Whisper",
            "formatted_title": "Careless Whisper",
            "image": "/static/images/cover/160.jpeg",
            "file_path": "/uploads/a188_careless_whisper.mp3"
        },
        {
            "id": 161,
            "title": "Nothings Gonna Change My Love For You",
            "formatted_title": " Nothings Gonna Change My Love For You",
            "image": "/static/images/cover/161.jpeg",
            "file_path": "/uploads/a189_Nothings_Gonna_Change_My_Love_For_You_-_Music_Travel_Love_ft._Bugoy_Drilon.mp3"
        },
        {
            "id": 162,
            "title": "Stuck On You",
            "formatted_title": "Stuck On You ",
            "image": "/static/images/cover/162.jpeg",
            "file_path": "/uploads/a190_-_Stuck_On_You_by_Lionel_Richie_Cover_1.mp3"
        },
        {
            "id": 163,
            "title": "If I Aint Got You Lyrics",
            "formatted_title": "If I Aint Got You ",
            "image": "/static/images/cover/163.jpeg",
            "file_path": "/uploads/a191_If_I_Aint_Got_You_Lyrics.mp3"
        },
        {
            "id": 164,
            "title": "Minefields",
            "formatted_title": "Minefields ",
            "image": "/static/images/cover/164.jpeg",
            "file_path": "/uploads/a192_Minefields_Official_Music_Video.mp3"
        },
        {
            "id": 165,
            "title": "Shallow",
            "formatted_title": " Shallow ",
            "image": "/static/images/cover/165.jpeg",
            "file_path": "/uploads/a193-_Shallow_cover.mp3"
        },
        {
            "id": 166,
            "title": "You Are The Reason",
            "formatted_title": " You Are The Reason",
            "image": "/static/images/cover/166.jpeg",
            "file_path": "/uploads/a194_You_Are_The_Reason_-_Luke_Silva__Elisa_Astrid_Calum_Scott_Cover.mp3"
        },
        {
            "id": 167,
            "title": "Older",
            "formatted_title": " Older ",
            "image": "/static/images/cover/167.jpeg",
            "file_path": "/uploads/a195_Older_Lyric_Video.mp3"
        },
        {
            "id": 168,
            "title": "Grow As We Go",
            "formatted_title": " Grow As We Go ",
            "image": "/static/images/cover/168.jpeg",
            "file_path": "/uploads/a196-_Grow_As_We_Go_feat._Sara_Bareilles_Official_Audio.mp3"
        },
        {
            "id": 169,
            "title": "Coastline",
            "formatted_title": "Coastline",
            "image": "/static/images/cover/169.jpeg",
            "file_path": "/uploads/a197_Coastline_Lyrics.mp3"
        },
        {
            "id": 171,
            "title": "Its Always Been You",
            "formatted_title": "A199  Its Always Been You Official Lyric Video",
            "image": "/static/images/cover/171.jpeg",
            "file_path": "/uploads/a199-_Its_Always_Been_You_Official_Lyric_Video.mp3"
        },
        {
            "id": 172,
            "title": "On Purpose",
            "formatted_title": "On Purpose ",
            "image": "/static/images/cover/172.jpeg",
            "file_path": "/uploads/a200_On_Purpose_Official_Music_Video.mp3"
        },
        {
            "id": 173,
            "title": "Rolling in the Deep ",
            "formatted_title": "A51 Rolling In The Deep Official Music Video",
            "image": "/static/images/cover/173.jpeg",
            "file_path": "/uploads/A51_Rolling_in_the_Deep_Official_Music_Video.mp3"
        }
    ]
# Serve files from the uploads directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)

@app.route('/user')
def user():
    return render_template('user.html', songs=songs)


# Lazy load the models (loads only when needed)
def load_models():
    try:
        lda = joblib.load('C:\\Users\\nur_e\\EmoSync\\models\\lda2.pkl')
        neural_network_model = tf.keras.models.load_model('C:\\Users\\nur_e\\EmoSync\\models\\best_model2.h5')
        scaler = joblib.load('C:\\Users\\nur_e\\EmoSync\\models\\scaler.pkl')
        return lda, neural_network_model, scaler
    except Exception as e:
        logging.error(f"Error loading models: {e}")
        raise

# Function to recommend similar songs
# In your recommend_random_top_similar_songs function
def recommend_random_top_similar_songs(song_id, data, similarity_df, num_recommendations=10):
    if song_id not in similarity_df.index:
        raise ValueError(f"Song ID '{song_id}' not found in the dataset.")
    
    similar_songs = similarity_df[song_id][similarity_df[song_id] == 1.0]
    similar_songs = similar_songs.drop(song_id, errors='ignore')
    
    # Get a random sample of similar songs
    random_recommendations = similar_songs.sample(n=min(num_recommendations, len(similar_songs)), random_state=None)
    
    # Mapping song titles, images, and file paths
    song_titles = data.set_index('song_id')['Song Tittle ']
    recommendations = pd.DataFrame({
        'song_id': random_recommendations.index,
        'song_title': random_recommendations.index.map(song_titles),
        'similarity_score': random_recommendations.values,
        # Path to cover image
        'image': random_recommendations.index.map(lambda id: f"/static/images/cover/{id}.jpeg"),
        # Path to song file
        'file_path': random_recommendations.index.map(lambda id: f"/static/music2/{id}.mp3")
    })
    
    return recommendations

# Home page route
@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/try')
def index2():
    return render_template('results2.html')

def analyze_lyrics_with_groqcloud(lyrics_text):
    # Create Groq client instance with API key from environment variable
    client = Groq(api_key=os.environ.get("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"))
    
    # Craft the request for an emotional interpretation of the lyrics
    prompt_content = (
        "Interpret the following lyrics emotionally and provide analysis "
        "of the emotions and meanings embedded in the lyrics. Summarize short and concise in few sentences :\n" + lyrics_text
    )

    # Prepare the chat completion request
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            model="llama3-8b-8192",
        )
        
        # Extract and return the response message content, assuming it's a detailed analysis
        return {"interpretation": chat_completion.choices[0].message.content}
    except Exception as e:
        logging.error(f"GroqCloud request failed: {e}")
        return {"interpretation": "Unable to retrieve an emotional interpretation for these lyrics."}

def analyze_rhythm_with_groqcloud(rhythm_segment_features):
    # Initialize Groq client
    client = Groq(api_key=os.environ.get("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"))

    # Craft the prompt for rhythm feature emotional analysis
    prompt_content = (
        "Interpret the following rhythm segment features emotionally and provide an "
        " analysis of the emotions these features might convey and Summarize short and concise in few sentences:\n" + str(rhythm_segment_features)
    )

    # Request emotional interpretation from Groq
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_content}],
            model="llama3-8b-8192",
        )
        return {"interpretation": chat_completion.choices[0].message.content}
    except Exception as e:
        logging.error(f"GroqCloud request failed: {e}")
        return {"interpretation": "Unable to retrieve an emotional interpretation for these rhythm features."}

@app.route('/analyze/rhythm/<int:song_id>')
def analyze_rhythm(song_id):
    logging.info(f"Received request to analyze song with ID: {song_id}")
    song = next((song for song in songs if song['id'] == song_id), None)
    
    if not song:
        logging.error(f"Song with ID {song_id} not found.")
        flash("Song not found.")
        return redirect(url_for('home'))
    
    # Store current song in session
    session['current_song'] = {
        "title": song["title"],
        "file_path": song["file_path"],
        "album_art": song["image"]
    }

    # Get the song's file path
    file_path = os.path.join(UPLOADS_DIR, os.path.basename(song['file_path']))
    if not os.path.exists(file_path):
        logging.error(f"File not found at {file_path}")
        flash("Song file not found.")
        return redirect(url_for('home'))
    
    try:
        # Rhythm analysis
        rhythm_features = extract_rhythm_features(file_path)
        predicted_rhythm_emotion = None
        rhythm_analysis = {}  # Initialize as a dictionary to store segment analysis

        # If rhythm features are extracted, analyze each segment
        if rhythm_features:
            lda, neural_network_model, scaler = load_models()
            predicted_rhythm_emotion = predict_rhythm_emotion(
                rhythm_features,
                lda_path='C:\\Users\\nur_e\\EmoSync\\models\\lda2.pkl',
                model_path='C:\\Users\\nur_e\\EmoSync\\models\\best_model2.h5',
                scaler_path='C:\\Users\\nur_e\\EmoSync\\models\\scaler.pkl'
            )

            # Analyze each rhythm segment with Groq
            for segment_id, segment_features in enumerate(rhythm_features, start=1):
                interpretation = analyze_rhythm_with_groqcloud(segment_features)
                rhythm_analysis[f"Segment {segment_id}"] = interpretation

        # Load dataset for recommendations
        data = pd.read_csv('C:\\Users\\nur_e\\EmoSync\\data\\music.csv')
        # Ensure all necessary columns are present for recommendations
        if {'Rhythm Segment 1', 'Rhythm Segment 2', 'Rhythm Segment 3', 'Rhythm Segment 4', 'Rhythm Segment 5'}.issubset(data.columns):
            data['Rhythm Mode'] = data[['Rhythm Segment 1', 'Rhythm Segment 2', 'Rhythm Segment 3', 'Rhythm Segment 4', 'Rhythm Segment 5']].mode(axis=1)[0]
        
        # Initialize recommendations as None in case similarity calculations fail
        recommended_songs = None

        if {'Lyrics Emotion', 'Rhythm Mode'}.issubset(data.columns):
            # Calculate similarities and get recommended songs
            lyrics_similarity = cosine_similarity(data[['Lyrics Emotion']].fillna(0))
            rhythm_similarity = cosine_similarity(data[['Rhythm Mode']].fillna(0))
            hybrid_similarity_df = pd.DataFrame(
                lyrics_similarity * 0.6 + rhythm_similarity * 0.4,
                index=data['song_id'], columns=data['song_id']
            )
            recommended_songs = recommend_random_top_similar_songs(song_id, data, hybrid_similarity_df, num_recommendations=10)

 # Store recommended songs in session for frontend access
            session['recommended_songs'] = recommended_songs.to_dict(orient='records')
        # Lyrics analysis with Genius API and GroqCloud
        formatted_title = song.get("formatted_title")
        lyrical_features = {"Lyrics": "Lyrics not found"}
        predicted_lyrics_emotion = "Lyrics not available for analysis."

        if formatted_title:
            # Fetch song lyrics using Genius API
            genius_song = genius.search_song(formatted_title)
            if genius_song and genius_song.lyrics:
                lyrical_features["Lyrics"] = genius_song.lyrics

                # Analyze lyrics with GroqCloud for interpretation insights
                groqcloud_insights = analyze_lyrics_with_groqcloud(genius_song.lyrics)
                if isinstance(groqcloud_insights, dict):
                    lyrical_features["interpretation"] = analyze_lyrics_with_groqcloud(genius_song.lyrics).get("interpretation")

                # Predict lyrics emotion using ML model
                try:
                    predicted_lyrics_emotion = predict_lyrics_emotion(lyrical_features["Lyrics"])
                except Exception as e:
                    logging.error(f"Prediction failed for '{formatted_title}': {e}")
                    predicted_lyrics_emotion = "Emotion prediction was not successful."

        # Render template with results
        return render_template(
            'results2.html',
            rhythm_features=rhythm_features,
            rhythm_analysis=rhythm_analysis,  # Updated to include Groq analysis of each segment
            lyrical_features=lyrical_features,
            song=song,
            predicted_rhythm_emotion=predicted_rhythm_emotion,
            predicted_lyrics_emotion=predicted_lyrics_emotion,
            recommended_songs=recommended_songs.to_dict(orient='records') if recommended_songs is not None else None
        )
    
    except Exception as e:
        logging.error(f"Error during combined analysis for song ID {song_id}: {e}")
        flash("An error occurred during analysis.")
        return redirect(url_for('home'))

@app.route('/recommended-songs')
def get_recommended_songs():
    recommended_songs = session.get('recommended_songs')
    return jsonify(recommended_songs) if recommended_songs else jsonify([])


@app.route('/current-track')
def current_track():
    song = session.get('current_song')
    if song:
        # Update file_path with URL accessible by the frontend
        song["file_path"] = url_for('uploaded_file', filename=os.path.basename(song["file_path"]))
        return jsonify(song)
    else:
        return jsonify({
            "title": "No song selected",
            "file_path": "",
            "album_art": "/static/images/b3.png"
        })

@app.route('/get-lyrics', methods=['GET'])
def get_lyrics():
    """Fetch lyrics for a given song using the Genius API."""
    song_title = request.args.get('song')
    artist_name = request.args.get('artist', '')

    if not song_title:
        return jsonify({"error": "Song title is required"}), 400

    try:
        # Search for the song on Genius
        genius_song = genius.search_song(song_title, artist_name)
        if genius_song and genius_song.lyrics:
            return jsonify({"lyrics": genius_song.lyrics})
        else:
            return jsonify({"error": "Lyrics not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching lyrics for '{song_title}': {e}")
        return jsonify({"error": "An error occurred while fetching lyrics"}), 500


if __name__ == '__main__':
    app.run(debug=True)