# Quick Start
## Install Dependency
```
pip install tornado
pip install redis
pip install celery
pip install requests
pip install mock
```
## Run web server (from project root dir)
```
python app/web_main.py
```
## Run Redis
```
redis-server
```
## Run downloader (from project root dir)
```
celery -A app.offline worker
```
## Run periodic scanner (from project root dir)
```
celery -A app.retry worker -B
```
# Object
## Resource
```
{
    'url': 'http://wx3.sinaimg.cn/large/a905b8d7gy1fhut64hn53j20c803sq35.jpg',
    'size': 1024, // unit: Byte
    'status': 'init', // 'init', 'done', 'failed'
    'mimetype': 'image/jpg',
    'created': 1501059062.889664, // timestamp, unit: second
    'task_id': '3ac30f26-eb1f-44b3-abf0-cc98a049ba6d',
    'downloaded': 0,
    'downloaded_time': 1501059063.889664, // timestamp, unit: second
    'content_hash': '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
}
```
# WEB API
## Capture a resource by url
```
POST /capture
```
### Example Input
```
{
    "url": "http://wx3.sinaimg.cn/large/a905b8d7gy1fhut64hn53j20c803sq35.jpg"
}
``` 
### Response
```
Status: 201 Created
```
## Capture resources by urls (batch API) 
```
POST /batch/capture
```
### Example Input
```
{
    "urls": [
        "http://wx3.sinaimg.cn/large/a905b8d7gy1fhut64hn53j20c803sq35.jpg",
        "http://wx1.sinaimg.cn/large/88c184bcgy1fhvv8kjkrxg20a006p7ws.gif",
    ]
}
``` 
### Response
```
Status: 201 Created
```
## Get resources by status
```
GET /resources?status=[done|ongoing|failed]
```
### Response
```
[
    Resource,
    ...
]
```
## Get resource by url
```
GET /resources/http%3A%2F%2Fwx3.sinaimg.cn%2Flarge%2F88c184bcgy1fhw3tusgejj20hr0vk43k.jpg
```
### Response
```
Resource
```
# Download task life cycle
1. get a url
2. check url if already downloaded -> task finish
3. check if domain blacklisted us -> task store at failed list
4. send a http get request in stream mode
5. check the status code -> 403: task store at failed list !200: task finish
6. check the file size and type -> task finish
7. created a record
8. download the resource -> exception: task store at failed list
9. write to dish -> exception: task store at failed list
10. update record
