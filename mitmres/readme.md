### 使用方法

> rewrite.yaml 
   
path配置文件，根据指定path进行rewrite操作

```yaml
'@all': # 公共配置的headers
   request:
     headers:
       h1: h1
/x/path/info: # 指定path路径的配置，content是mock的响应内容
  request:
    headers:
      h2: h2
  response:
    headers:
      h3: h3
    content: {'status': 0}

```

> response/xxx.json 
   
rewrite response文件夹，在rewrite.yaml中配置xxx.json

