# Duolingo_backend

#### 开发环境
port: 8000

#### 生产环境
port: 
Django:8101

#### 运行说明
**开发**

运行环境
`python home/set_env.py {dev/prod}`

启动服务：
`DJANGO_ENVIRONMENT={dev/prod} python manage.py runserver 0.0.0.0:8101`

启动celery 工作者：
`DJANGO_ENVIRONMENT={dev/prod} celery -A home worker --loglevel=info`

启动celery 定时任务：
`DJANGO_ENVIRONMENT={dev/prod} celery -A home beat --loglevel=info --schedule=/tmp/celerybeat-schedule`

同时启动 Beat 和 Worker：
celery -A home worker -B --loglevel=info


**生产**
`sudo systemctl restart duolingo_celery_worker`
`sudo systemctl restart duolingo_celery_beat`

## 分支说明
#### main
主要分支

#### dev
开发分支

## 更新方案

1. 切换到 目录
```bash
cd /home/Duolingo/backend
```

2. 拉取最新代码
```bash
git pull
```

3. 重启 Django 服务
```bash
sudo systemctl restart duolingo_django_gunicorn
```

### 一键更新脚本
```bash
cd /home/Duolingo/backend && \
git pull && \
source .venv/bin/activate && \
python home/set_env.py prod && \
DJANGO_ENVIRONMENT=prod python manage.py migrate && \
sudo systemctl restart duolingo_django_gunicorn && \
sudo systemctl restart duolingo_celery_beat && \
sudo systemctl restart duolingo_celery_worker
```