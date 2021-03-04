# ctfd-dynamic_instance
#####          A pulgin for ctfd to support Dynamic docker instances. 

​		本人是一个菜鸡ctf-web选手,由于会在buuctf,bugku这样的ctf靶场做题,所以看着人家的动态靶机很眼馋.借鉴了buu的赵师傅的思路,自己也写了一个,功能上还比较简单,题目采用了沙漏积分,即一血获取全部分数,题目解决人数每增加一人,答对题目所获得的分数递减,直至减至所设的下限为止

### 界面

![image-20210228151451653](https://tva1.sinaimg.cn/large/e6c9d24ely1go3etl77quj21h90u0tg7.jpg)

![image-20210228151507978](https://tva1.sinaimg.cn/large/e6c9d24ely1go3euoths0j21kz0u0af0.jpg)

![image-20210228151526184](https://tva1.sinaimg.cn/large/e6c9d24ely1go3eurmm4lj21kr0u0799.jpg)

![image-20210228151550144](https://tva1.sinaimg.cn/large/e6c9d24ely1go3ev62nm1j21pd0u0di2.jpg)

### 部署

文件结构:

```shell
├── README.md
└── dynamic_instance #插件目录
    ├── __init__.py #定义了路由
    ├── assets #前端
 	  │   ├── config.js
    │   ├── create.html
    │   ├── create.js
    │   ├── update.html
    │   ├── update.js
    │   ├── view.html
    │   └── view.js
    ├── certs #储存了远程docker api的证书和秘钥
    │   ├── 7815696ecbf1c96e6894b779456d330e
    │   │   ├── cert.pem
    │   │   └── key.pem
    │   └── f7ec3bbcc8333d6febfb93014cea36cd
    │       ├── cert.pem
    │       └── key.pem
    ├── config.json #ctfd插件所规定的配置json文件
    ├── plugin_config.json#储存插件设置的json文件
    ├── requirements.txt#python第三方扩展库
    ├── dockerutils.py#连接docker远程api
    ├── models.py#Flask-SQLAlchemy 
    └── utils.py#utils
```

​	安装python第三方库: `requirements.txt`在`dynamic_instance`目录下

```shell
pip install -r requirements.txt
```

​	部署时将本目录下的`dynamic_instance`拷贝至CTFd的`CTFd/plugins/`目录下即可

启动ctfd时插件将随之启动

![image-20210228154456825](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evak4mbj21n10u07wj.jpg)



### 配置

以admin用户打开CTFd中的Admin Panel菜单栏,选择plugins中的dynamic_instance

![image-20210228154717387](https://tva1.sinaimg.cn/large/008eGmZEly1go7zevb2abj31ks07wmy8.jpg)

下拉页面至`Config`部分

![image-20210228154905960](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evc3x6dj21ql0u0aeb.jpg)

在此可以选择`是否使用本地服务器`,`实例存活的时间`,`每次延长的时间`以及`实例最大的存活时间`

### 添加远程docker API

此插件采用docker remote API来连接服务器上的docker服务,需要配置TLS加密通讯,具体配置方法可以参考http://oriole.fun/index.php/archives/24/

各项内容如下图:

![image-20210228161821146](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evfaimij21r20u0wjt.jpg)

### 创建题目镜像

创建题目镜像是为了在添加题目时直接引用,题目镜像需要提前上传至dockerhub或其他公开的镜像仓库

具体内容如下图

![image-20210228162308728](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evjkpn0j21lb0u0gsm.jpg)



### 添加题目

添加动态靶机题目的入口和ctfd其他类型题目的添加入口在同处

动态靶机题目需要单独设置的内容如下

![image-20210228162925519](https://tva1.sinaimg.cn/large/e6c9d24ely1go3fuexzaoj21dc0u0wjo.jpg)

### 题目界面

![image-20210228163249926](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evn7rg3j20ti0qs762.jpg)

![image-20210228163424274](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evpzr87j20to136gpt.jpg)

