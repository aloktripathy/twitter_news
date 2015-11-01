rsync -r /home/code/twitter_news/static/* /var/www/html/twitter_news
git pull
gunicorn twitter_news.wsgi -b 127.0.0.1:8001 -D