import streamlit as st
import requests

# Define constants
BASE_URL = "https://api.bing.microsoft.com/v7.0/search"
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

            # Save sitemap to file and give user link to download
            filename = f"{query.replace(' ', '_')}.xml"
            st.write(f"Saving sitemap to file: {filename}")

            with open(filename, "w") as f:
                f.write(sitemap)

            # Display sitemap for debugging purposes
            st.markdown(f"Sitemap generated! Download <a href='https://armaangis-streamlit-bingsearchsitemap-app-gkp1c8.streamlit.app/{filename}' download target='_blank'>here</a>.", unsafe_allow_html=True)
            st.download_button('Download', sitemap)  # Defaults to 'text/plain'
            st.experimental_set_query_params(sitemap)

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed with error {e}")
    except KeyError:
        st.error("Invalid response format")
