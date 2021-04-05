#-*- coding:utf-8 -*-
import os
import docker
from .models import *
from CTFd.models import Challenges, db
import time
from.dockerutils import Instance
import json
import sqlite3
#from apscheduler.schedulers.blocking import BlockingScheduler
#from apscheduler.schedulers.background import BackgroundScheduler

def delete(dir):
    if os.path.isdir(dir):  # dir是目录
        list_1 = os.listdir(dir)
        if not list_1:
            os.rmdir(dir)  # 空目录直接删除
        else:  # 非空目录
            for index, i in enumerate(list_1):
                # 获得目录下所有目录及文件的绝对路径
                list_1[index] = os.path.join(dir, i)

            for i in list_1:
                if os.path.isfile(i):  # 是文件直接删除
                    os.remove(i)
                else:  # 是目录循环继续执行本函数
                    delete(i)
            os.rmdir(dir)
    else:  # dir是文件
        os.remove(dir)   
def load_config():
    with open("CTFd/plugins/dynamic_instance/plugin_config.json",'r') as f:
        return json.load(f)


def remove_timeout():
    #print("INFO [plugin] Remove timeout instances")
    conn=sqlite3.connect("CTFd/ctfd.db")
    cusor=conn.cursor()
    cusor.execute("SELECT imagename,containerid,id FROM instances  WHERE endtime <={} ;".format(time.time()))
    select_timeout=cusor.fetchall()
    if select_timeout:
        for instance in select_timeout:
            id=instance[2]
            containerid=instance[1]
            cusor.execute("SELECT pullimage FROM challenge_images WHERE name='{}';".format(instance[0]))
            select_servertag=cusor.fetchone()
            servertag=select_servertag[0]
            print(servertag)
            cusor.execute("SELECT socket,client_cert_file,client_key_file FROM servers  WHERE tag ='{}' ;".format(servertag))
            socket,client_cert_file,client_key_file=cusor.fetchone()
            if servertag=="local":
                try:
                    client=docker.from_env()
                except Exception as e:
                    print(e)
                    return e
            else:
                tls_config = docker.tls.TLSConfig(client_cert=(client_cert_file,client_key_file))
                try:
                    client=docker.DockerClient(base_url=socket,tls=tls_config)
                except Exception as e:
                    print(e)
                    return e
            try:
                container=client.containers.get(containerid)
                container.stop()
                container.remove()
            except Exception as e:
                    print(e)
                    return e
            cusor.execute("DELETE FROM instances WHERE id={}".format(id))
            conn.commit()
            conn.close()
    conn.close()
    return


def pull_image(servertag,RepoTags):
    conn=sqlite3.connect("CTFd/ctfd.db")
    cusor=conn.cursor()
    cusor.execute("SELECT socket,client_cert_file,client_key_file FROM servers  WHERE tag ='{}' ;".format(servertag))
    socket,client_cert_file,client_key_file=cusor.fetchone()
    if servertag=="local":
        try:
            client=docker.from_env()
        except Exception as e:
            print(e)
            return e
    else:
        tls_config = docker.tls.TLSConfig(client_cert=(client_cert_file,client_key_file))
        try:
            client=docker.DockerClient(base_url=socket,tls=tls_config)
        except Exception as e:
            print(e)
            return e
    try:
        if client.images.list(name=RepoTags):
            image=client.images.get(RepoTags)
            imageid=image.id
            imageid=imageid.replace('sha256:','')
            size=int(int(image.attrs['Size'])/1048576)
            cusor.execute(f"UPDATE challenge_images SET imageid='{imageid}',size={size},pulled=1 WHERE RepoTags='{RepoTags}';")
            conn.commit()
            conn.close()
            return
        repo=RepoTags[0:RepoTags.index(':')]
        tag=RepoTags[RepoTags.index(':')+1:]
        image=client.images.pull(repo,tag)
        imageid=image.id
        imageid=imageid.replace('sha256:','')
        size=int(int(image.attrs['Size'])/1048576)
        cusor.execute(f"UPDATE challenge_images SET imageid='{imageid}',size={size},pulled=1 WHERE RepoTags='{RepoTags}';")
        conn.commit()
        conn.close()
        return
    except Exception as e:
            print(e)
            return e
    