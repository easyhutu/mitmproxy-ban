# mitmproxy-ban

> 基于 [mitmproxy:v8.1.1](https://github.com/mitmproxy/mitmproxy/archive/refs/tags/v8.1.1.tar.gz
)

免责声明：***仅限用于学习和参考***

### 目的
主要对mitmproxy做一些优化，符合国内用户使用习惯

### 优化功能点

1. 限制flows数量，防止flows请求记录太多导致浏览器卡顿
2. web端默认请求记录倒序排列，瀑布式展示请求记录，符合日常使用习惯
3. mitmweb 页脚显示当前ip地址，设置代理更方便
4. 增加默认rewrite headers，response 配置文件，方便操作

### 安装方法
* 源码安装

下载项目，进入根目录执行：
```shell
python setup.py install
```

* 渠道安装

```shell
pip install mitmproxy-ban
```