# ctfd-dynamic_ instance
#####          A pulgin for ctfd to support Dynamic docker instances.
​    The challenge adopts hourglass score, that is, one blood gets all the scores. The number of problem solving personnel increases, and the score obtained by the correct answer is decreased, Until it is reduced to the lower limit set

### Interface
![image-20210228151451653](https://tva1.sinaimg.cn/large/e6c9d24ely1go3etl77quj21h90u0tg7.jpg )
![image-20210228151507978]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3euoths0j21kz0u0af0.jpg )

![image-20210228151526184]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3eurmm4lj21kr0u0799.jpg )
![image-20210228151550144]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3ev62nm1j21pd0u0di2.jpg )

 ### Deploy
File structure:

```shell
├──  README.md
└── dynamic_ Instance plug-in directory
├── __ init__ .py defines routing routes
├── assets
│   ├──  config.js
│   ├──  create.html
│   ├──  create.js
│   ├──  update.html
│   ├──  update.js
│   ├──  view.html
│   └──  view.js
├── certs 
│   ├── 7815696ecbf1c96e6894b779456d330e
│   │   ├──  cert.pem
│   │   └──  key.pem
│   └── f7ec3bbcc8333d6febfb93014cea36cd
│       ├──  cert.pem
│       └──  key.pem
├──  config.json  #Configuration JSON file specified by ctfd plug-in
├── plugin_ config.json# Store JSON files for plug-in settings
├──  requirements.txt#python Third party extension library
├──  dockerutils.py# Connect docker remote API
├──  models.py#Flask -SQLAlchemy
└──  utils.py#utils
```
Install Python third party Library:` requirements.txt `In `dynamic_ Instance 'directory
```shell
pip install -r  requirements.txt
```
When deployed, the dynamic_ Instance 'copy to ctfd's' ctfd/plugins/' directory
The plug-in will start when ctfd is started
![image-20210228154456825]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3evak4mbj21n10u07wj.jpg )



### Configuration
Open the admin panel menu bar in ctfd by admin user, and select dynamic in plugins_ instance
![image-20210228154717387]( https://tva1.sinaimg.cn/large/008eGmZEly1go7zevb2abj31ks07wmy8.jpg )

Drop down to the 'config' section
![image-20210228154905960]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3evc3x6dj21ql0u0aeb.jpg )
Here, you can choose whether to use local server, time of instance survival, time of extension each time and maximum lifetime of instance`

### Add remote docker API
This plug-in uses docker remote API to connect to docker service on the server. TLS encryption communication needs to be configured. Please refer to the specific configuration method http://oriole.fun/index.php/archives/24/
The contents are as follows:



![image-20210228161821146](https://tva1.sinaimg.cn/large/e6c9d24ely1go3evfaimij21r20u0wjt.jpg )

### Create a title image
The title image is created to directly reference when adding a title. The title image needs to be uploaded to dockerhub or other public image warehouse in advance
The details are as follows
![image-20210228162308728]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3evjkpn0j21lb0u0gsm.jpg )



### Add a challnge
The entry of adding dynamic target subject and other types of ctfd are in the same place
The following contents are required to be set separately for the dynamic target
![image-20210228162925519]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3fuexzaoj21dc0u0wjo.jpg )



### Title Challenge Pannel
![image-20210228163249926]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3evn7rg3j20ti0qs762.jpg )

![image-20210228163424274]( https://tva1.sinaimg.cn/large/e6c9d24ely1go3evpzr87j20to136gpt.jpg )