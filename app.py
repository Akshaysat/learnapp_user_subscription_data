import requests
import json
import pandas as pd
import time
import datetime as dt
import streamlit as st

# Kraken Auth Token
url = "https://e3d72bp6aa.execute-api.ap-south-1.amazonaws.com/"
payload = {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
access_token = response.text

token = "Bearer " + access_token


def fetch_userid(email):
    email = email.replace("@", "%40")
    url = "https://hydra.prod.learnapp.com/kraken/users/search?q=" + email

    payload = {}
    headers = {
        "authorization": token,
        "x-api-key": "u36jbrsUjD8v5hx2zHdZNwqGA6Kz7gsm",
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    try:
        data = json.loads(response.text)["users"][0]
        try:
            return data["userId"]
        except:
            return -1
    except:
        return -1


# If the user has subscribed to LearnApp or not
def user_access(email):
    email = email.strip().lower()

    flag = False
    today_date = dt.datetime.now().strftime("%Y-%m-%d")

    try:
        userid = fetch_userid(email)
        url = "https://hydra.prod.learnapp.com/kraken/users/" + str(userid)

        payload = {}

        headers = {
            "authorization": token,
            "x-api-key": "u36jbrsUjD8v5hx2zHdZNwqGA6Kz7gsm",
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = json.loads(response.text)["accessPolicy"]

        for i in data:
            if i["type"] == "BASE_PLAN":
                expiry_dates = []
                subs = i["access"]
                for j in subs:
                    expiry_date = j["expiry"][:10]
                    expiry_dates.append(expiry_date)

                latest_expiry_date = max(expiry_dates)

                if latest_expiry_date > today_date:
                    flag = "active"
                    break
                else:
                    flag = "expired"
                    break

        if flag == "active":
            return "Paid User"

        elif flag == "expired":
            return "Expired User"

        else:
            return "Non Paid User"

    except:
        if userid == -1:
            return "Non LA User"
        else:
            return "Non Paid User - issue"


# Frontend
col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("black_logo.png", width=225)
    st.write("")
with col3:
    st.write("")

st.write("----")

st.markdown(
    "<h2 style='text-align: center; color: black;'>Get subscription status of LA users</h2>",
    unsafe_allow_html=True,
)

st.write("----")
# Code to get the list of users
user_data = st.file_uploader("Upload a csv file with the Email ID of users")


st.write("")

# Code to get the subscription data of users
if st.button("Find Completion %"):

    user_data = pd.read_csv(user_data)

    with st.spinner("Fetching Data From Kraken ..."):
        st.write("-----")

        user_data["status"] = user_data["Email"].apply(user_access)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Paid Users", (user_data["status"] == "Paid User").sum())

        with col2:
            st.metric("Expired Users", (user_data["status"] == "Expired User").sum())

        with col3:
            st.metric("Non-Paid Users", (user_data["status"] == "Non Paid User").sum())

        with col4:
            st.metric("Non LA User", (user_data["status"] == "Non LA User").sum())

        st.write("")

        @st.cache
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")

        csv = convert_df(user_data)

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="user_data.csv",
            mime="text/csv",
        )

        st.write("-----")

        st.dataframe(user_data)
