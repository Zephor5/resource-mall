# resource-mall
no description


###资源支持


- mysql
- redis [开发中]


###特点
- REST风格API提供
- 分布式多机支持
- 自动规划资源，动态资源分配
- 自定义资源配置参数支持


###项目结构
- server_api 接口提供程序，可以基于nginx+uwsgi方式部署
- daemon_host 资源提供机器守护程序，用于自动将程序所在主机加入资源分配池，接收另外两个模块的控制命令
- daemon_manager 【待完成】资源池守护进程，用于监控资源池状态，清理失效资源，同时通知用户，重新动态更新用户资源等


###依赖
- mac or linux
- python2.7
- mongodb
- docker


###安装
- 单机开发环境
  - 准备好依赖环境
  - 下载代码
  - 修改配置选项 `configs/dev/` 相关
  - `virtualenv .env`
  - `source .env/bin/activate`
  - `pip install -r requirements.txt -r requirements-test.txt`
  - `pytest .`
  - `python daemon_host.py 1> dev_daemon_host.log 2> dev_daemon_host.err &`
  - `python server_api.py 1> dev_server_api.log 2> dev_server_api.err &`

- 调用示例
  - `curl -i -X POST -H "Content-Type:application/json" -d '{"version":"5.5", "charset": "utf8", "engine": "MYISAM", "mem_size": 100, "storage_size": 1000, "cpu_freq": 500}' 'http://127.0.0.1:8888/resource/mysql'`

- 分布式部署
  - 单机部署server_api 可选 daemon_host
  - 资源承载机器部署 daemon_host
