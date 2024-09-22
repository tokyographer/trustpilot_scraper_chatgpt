import streamlit as st
import requests
from bs4 import BeautifulSoup
import logging
import time

# Function to scrape reviews from multiple pages of Trustpilot
def scrape_reviews(url):
    try:
        reviews = []
        page = 1  # Start from the first page
        more_reviews = True
        reviews_per_page = 20  # Trustpilot typically shows 20 reviews per page
        total_reviews = 57  # You can estimate the total number of reviews if known
        
        # Progress bar setup
        progress_bar = st.progress(0)
        time.sleep(0.2)

        while more_reviews:
            # Modify the URL to include the page number
            paginated_url = f"{url}&page={page}"
            response = requests.get(paginated_url)

            if response.status_code == 404:
                st.warning(f"No more pages found after page {page}.")
                break  # Exit the loop if a 404 error is encountered

            if response.status_code != 200:
                st.error(f"Failed to retrieve reviews from page {page}: Status Code {response.status_code}")
                return reviews  # Return the reviews collected so far

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find review elements based on the structure
            review_cards = soup.find_all("div", class_="styles_reviewCardInner__EwDq2")
            total_reviews_on_page = len(review_cards)

            # If no reviews are found on the current page, stop the loop
            if total_reviews_on_page == 0:
                more_reviews = False
                break

            for idx, review_card in enumerate(review_cards):
                # Extract the review title
                review_title = review_card.find("h2", class_="typography_heading-s__f7029").text if review_card.find("h2", class_="typography_heading-s__f7029") else "No title"
                
                # Extract the review text
                review_text = review_card.find("p", class_="typography_body-l__KUYFJ").text if review_card.find("p", class_="typography_body-l__KUYFJ") else "No review text"
                
                # Extract the rating (if available)
                rating_div = review_card.find("div", {"data-service-review-rating": True})
                rating = rating_div['data-service-review-rating'] if rating_div else "No rating"

                # Store the review details in a dictionary
                reviews.append({
                    "title": review_title,
                    "text": review_text,
                    "rating": rating,
                })

            # Update progress bar
            progress_percentage = min((page * total_reviews_on_page * 100 // total_reviews), 100)
            progress_bar.progress(progress_percentage)

            page += 1  # Move to the next page
            time.sleep(0.1)  # Simulate delay in scraping to avoid rate limiting

        # Completion alert
        st.success(f"Scraping complete! Collected {len(reviews)} reviews.")
        st.balloons()

        return reviews

    except Exception as e:
        logging.error(f"Error occurred while scraping reviews: {e}")
        st.error("An error occurred while scraping reviews.")
        return None

# Streamlit app code to use the scrape_reviews function
st.title("Trustpilot Review Scraper & ChatGPT Assistant")

trustpilot_url = st.text_input("Enter the Trustpilot URL to scrape reviews", "")

if trustpilot_url:
    st.write("Scraping reviews... Please wait.")
    reviews = scrape_reviews(trustpilot_url)

    if reviews:
        st.subheader("Scraped Reviews")
        for idx, review in enumerate(reviews):
            st.write(f"**Title**: {review['title']}")
            st.write(f"**Rating**: {review['rating']}")
            st.write(f"**Review**: {review['text']}")
            st.write("---")

# Output the total number of reviews
if trustpilot_url and reviews:
    st.write(f"Total number of reviews scraped: {len(reviews)}")