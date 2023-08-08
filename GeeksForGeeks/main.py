from playwright.sync_api import Playwright, sync_playwright, expect
import time
from dateutil import parser
import pandas as pd
import matplotlib.pyplot as plt


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.youtube.com/@GeeksforGeeksVideos/videos")

    

    # Wait for the page to load completely
    page.wait_for_selector('//*[@id="video-title"]')
    page.wait_for_selector('.style-scope ytd-rich-grid-media')


    counter = 3

    while counter > 0:
        prev_height = page.evaluate("document.documentElement.scrollHeight")
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        timeout_ms = 3000  # Wait for 3 seconds



        # Scrape video information using XPaths
        titles = page.query_selector_all('//*[@id="video-title"]')
        times = page.query_selector_all('//*[@id="metadata-line"]/span[2]')
        video_elements = page.query_selector_all('.style-scope ytd-rich-grid-media')
        links = page.query_selector_all(".style-scope ytd-grid-video-renderer #thumbnail")
        views = page.query_selector_all('//*[@id="metadata-line"]/span[1]')



        page.wait_for_timeout(timeout_ms)
        new_height = page.evaluate("document.documentElement.scrollHeight")
        
        if new_height == prev_height:
            break  # No more content to load, break the loop

        counter = counter - 1

    
    

    #Create lists to store video information
    titlee = []
    viewss = []
    Datee = []
    Linkk = []
    Durationn = []



    time = ''

    count = 0
    i=0
    while time != '7 months ago' and i < len(titles):
        title = titles[i].text_content()
        view_count = views[i].text_content()
        time = times[i].text_content()

        titlee.append(title)
        viewss.append(view_count)
        Datee.append(time)
        
        


        duration_element = video_elements[i].query_selector('.style-scope ytd-thumbnail-overlay-time-status-renderer')
        link_element = video_elements[i].query_selector('a')
        if link_element and duration_element:
            link = link_element.get_attribute('href')
            duration = duration_element.inner_text()

            Linkk.append(link)
            Durationn.append(duration)
            
            

        count+=1
        i+=1

    video_data = {
        "Video Title":titlee,
        "Views Count":viewss,
        "Duration":Durationn,
        "Released Date":Datee,
        "Link":Linkk
    }
    
    
    df = pd.DataFrame(video_data)
    df.to_csv('video_data.csv', index=False)
    print(df)



    

# Extract numeric views from the 'Views Count' column
    df = pd.DataFrame(video_data)

    # Function to convert views to numeric
    def convert_views(views):
        if 'K' in views:
            return float(views.replace('K views', '')) * 1000
        else:
            return float(views.replace(' views', ''))

    # Apply the function to 'Views Count' column
    df['Views Count'] = df['Views Count'].apply(convert_views)

    # Sort the DataFrame by 'Views Count' in descending order
    sorted_df = df.sort_values(by='Views Count', ascending=False)

    # Print the topic with the most views

    print('The most viewed topics with video title in the past 6 months:')
    for i in range(5):
        most_views_topic = sorted_df.iloc[i]['Video Title']
        most_views_count = sorted_df.iloc[i]['Views Count']
        print(f" {most_views_topic} ({most_views_count} views)")

    print("\n")



    # Function to convert duration to minutes
    def convert_duration(duration):
        parts = duration.split(':')
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1])/60
        elif len(parts) == 3:
            return int(parts[0])*60 + int(parts[1]) + int(parts[2])/60
        else:
            return 0

    # Apply the function to 'Duration' column
    df['Duration (minutes)'] = df['Duration'].apply(convert_duration)

    # Sort the DataFrame by 'Duration (minutes)' in descending order
    sorted_df = df.sort_values(by='Duration (minutes)', ascending=False)

    # Display the topic with the highest video length
    print("Topics with the highest video lengths:")
    for i in range(5):
        highest_duration_topic = sorted_df.iloc[i]['Video Title']
        highest_duration = sorted_df.iloc[i]['Duration']
        print(f" {highest_duration_topic} ({highest_duration})")


    def convert_duration(duration):
        parts = duration.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            total_minutes = hours * 60 + minutes
        else:
            minutes, seconds = map(int, parts)
            total_minutes = minutes
        return total_minutes

    df['Duration'] = df['Duration'].apply(convert_duration)

    
    plt.figure(figsize=(10, 6))
    plt.bar(df['Duration'], df['Views Count'],width=0.8, color='Green')
    #plt.bar(df['Video Title'], df['Views Count'], color='Green', label='Number of Views')
    
    plt.xlabel('Video Lenght(in Minutes)')
    plt.ylabel('Views')
    plt.title('Comparison between Number of Views and Video Length')
    

    plt.xticks(range(0, 90, 5))
    plt.yticks(range(0, 110000, 10000))

    plt.grid(True)
    plt.show()

    

    
    context.close()
    browser.close()



with sync_playwright() as playwright:
    run(playwright)
