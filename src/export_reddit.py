import requests
import csv
import json
import argparse


user_agent = 'YOUR_USER_AGENT'


# Get posts from a subreddit
def get_posts(subreddit_name, num_posts=10):
    url = f'https://www.reddit.com/r/{subreddit_name}/top.json'
    params = {'limit': num_posts}
    headers = {'User-Agent': user_agent}

    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    posts = response_json['data']['children']
    return posts

# Get comments for a post
def get_comments(post_id, num_comments=5):
    url = f'https://www.reddit.com/comments/{post_id}.json'
    params = {'limit': num_comments}
    headers = {'User-Agent': user_agent}

    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    comments = response_json[1]['data']['children']
    return comments

# Recursively get replies to a comment
def get_replies(comment, num_replies=3):
    try:
        replies = comment['replies']['data']['children'] if 'replies' in comment else []
        for reply in replies[:num_replies]:
            if(reply.get('kind') == "t1"):
                reply_data = reply['data']
                yield reply_data
                yield from get_replies(reply_data, num_replies)
    except Exception as e: 
        #TODO: Fix this, look into this. Are we missing some comments by ignoring this?
        pass
# Save data to CSV
def save_to_csv(data, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['type','author_id', 'id',  'parent_id', 'title', 'body','num_comments']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(data)

# Download data from a subreddit
def download_data(output_file, subreddit_name, num_posts=10, num_comments=5, num_replies=3):
    output_data = []

    # Fetch the top 'num_posts' posts from the subreddit
    posts = get_posts(subreddit_name, num_posts)
    
    for post in posts:
        post_data = post['data']
        post_id = post_data['id']
        title = post_data['title']
        body = post_data['selftext']
        total_comments = post_data['num_comments']
        output_data.append({
                    'type':'post',
                    'author_id': post_data['author_fullname'] or post_data['author'],
                    'id': post_data['name'],
                    #'subreddit_id':'',
                    'parent_id': '',
                    'title': title,
                    'body': body,
                    'num_comments':total_comments
                })
        # Fetch the top 'num_comments' comments for each post
        comments = get_comments(post_id, num_comments)
        for comment in comments:
            if(comment.get('kind') == "t1"):
                comment_data = comment['data']
                author_id = comment_data['author'] or comment_data['author_fullname']
                comment_id = comment_data['id'] 
                parent_id = comment_data['parent_id']
                body = comment_data['body']
                subreddit_id = comment_data['subreddit_id']

                # You can add additional logic to extract 'location' and 'source_ip' if available.
                # For this example, I'll leave them as empty strings.
                location = ''
                source_ip = ''

                output_data.append({
                    'type':'comment',
                    'author_id': author_id,
                    'id': comment_id,
                    #'subreddit_id': subreddit_id,
                    'parent_id': parent_id,
                    'title': '',
                    'body': body,
                    'num_comments':''
                })

                # Fetch the top 'num_replies' replies for each comment
                for reply_data in get_replies(comment_data, num_replies):
                    author_id = reply_data['author'] or reply_data['author_fullname']
                    reply_id = reply_data['id']
                    parent_id = reply_data['parent_id']
                    body = reply_data['body'],
                    #subreddit_id = reply_data['subreddit_id']

                    # You can add additional logic to extract 'location' and 'source_ip' if available.
                    # For this example, I'll leave them as empty strings.
                    location = ''
                    source_ip = ''

                    output_data.append({
                        'type':'reply',
                        'author_id': author_id,
                        'id': reply_id,
                        #'subreddit_id': subreddit_id,
                        'parent_id': comment_id,
                        'title': '',
                        'body': body,
                        'num_comments':''
                    })

    # Save the output data to a CSV file
    save_to_csv(output_data, output_file)


#python script.py python --num_posts 10 --num_comments 5 --num_replies 3 --output_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download data from a subreddit and save to CSV.')
    parser.add_argument('subreddit', help='Name of the subreddit to download data from')
    parser.add_argument('--num_posts', type=int, default=5, help='Number of top posts to fetch')
    parser.add_argument('--num_comments', type=int, default=3, help='Number of top comments per post to fetch')
    parser.add_argument('--num_replies', type=int, default=2, help='Number of replies per comment to fetch')
    parser.add_argument('--output_file', type=str, default='', help='Output file orefix', required=False)
    
    args = parser.parse_args()
    subreddit_name = args.subreddit
    num_posts = args.num_posts
    num_comments = args.num_comments
    num_replies = args.num_replies
    output_file = subreddit_name + '-' + args.output_file + '-reddit_data.csv'
    
    download_data(output_file, subreddit_name, num_posts, num_comments, num_replies)

