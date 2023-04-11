import streamlit as st
import requests
import base64

# Define constants
BASE_URL = "https://api.github.com"
MAX_RESULTS = 100

# Set up Streamlit app
st.title("Sitemap Generator")
query = st.text_input("Enter your query:")
if st.button("Generate Sitemap"):
    try:
        # Make API request
        headers = {"Ocp-Apim-Subscription-Key": st.secrets["BING_API_KEY"]}
        params = {
            "q": query,
            "count": MAX_RESULTS,
            "responseFilter": "Webpages",
            "textFormat": "HTML"
        }
        response = requests.get(BASE_URL, headers=headers, params=params)

        # Check response status code and content type
        if response.status_code != 200:
            st.error(f"API request failed with status code {response.status_code}")
        elif "application/json" not in response.headers.get("Content-Type"):
            st.error("Invalid response format")
        else:
            # Parse results and create sitemap
            results = response.json()
            sitemap = "<?xml version='1.0' encoding='UTF-8'?><urlset>"
            for result in results["webPages"]["value"]:
                sitemap += f"<url><loc>{result['url']}</loc></url>"
            sitemap += "</urlset>"

            # Encode sitemap in Base64
            sitemap_b64 = base64.b64encode(sitemap.encode("utf-8")).decode("utf-8")

            # Upload to GitHub and get URL
            endpoint = f"/repos/{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO']}/contents/{query.replace(' ', '_')}.xml"
            response = requests.put(
                BASE_URL + endpoint,
                headers={"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}, 
                json={
                    "message": f"Add {query.replace(' ', '_')}.xml",
                    "committer": {
                        "name": st.secrets['GITHUB_USERNAME'],
                        "email": st.secrets['GITHUB_EMAIL']
                    },
                    "content": sitemap_b64,
                    "branch": "main"
                }
            )
            if response.status_code != 201:
                st.error("Failed to upload sitemap to GitHub")
            else:
                # Get URL to file on GitHub and display to user
                file_url = response.json()["content"]["html_url"]
                st.markdown(f"Sitemap generated! Download <a href='{file_url}' download target='_blank'>here</a>.", unsafe_allow_html=True)

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed with error {e}")
    except KeyError:
        st.error("Invalid response format")
